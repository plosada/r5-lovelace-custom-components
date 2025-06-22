#!/usr/bin/env python3
"""
Script para actualizar automáticamente los componentes de Lovelace
desde sus repositorios originales.
"""

import json
import os
import requests
import subprocess
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComponentUpdater:
    def __init__(self, config_file: str = "components_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Carga la configuración de componentes desde el archivo JSON."""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Archivo de configuración {self.config_file} no encontrado")
            return {}
    
    def _save_version_info(self, component_name: str, version_info: Dict):
        """Guarda información de versión para un componente."""
        version_file = os.path.join(component_name, "version.json")
        os.makedirs(component_name, exist_ok=True)
        
        with open(version_file, 'w') as f:
            json.dump(version_info, f, indent=2)
    
    def _get_current_version(self, component_name: str) -> Optional[Dict]:
        """Obtiene la versión actual de un componente."""
        version_file = os.path.join(component_name, "version.json")
        try:
            with open(version_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def _get_latest_release(self, repo_url: str) -> Optional[Dict]:
        """Obtiene información del último release de un repositorio de GitHub."""
        # Extraer owner/repo de la URL
        parts = repo_url.replace("https://github.com/", "").split("/")
        if len(parts) < 2:
            logger.error(f"URL de repositorio inválida: {repo_url}")
            return None
        
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error al obtener release de {repo_url}: {e}")
            return None
    
    def _get_latest_commit(self, repo_url: str, branch: str = "master") -> Optional[Dict]:
        """Obtiene información del último commit de un repositorio."""
        parts = repo_url.replace("https://github.com/", "").split("/")
        if len(parts) < 2:
            return None
            
        owner, repo = parts[0], parts[1]
        api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{branch}"
        
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Intentar con rama 'main' si 'master' falla
            if branch == "master":
                return self._get_latest_commit(repo_url, "main")
            logger.error(f"Error al obtener commit de {repo_url}: {e}")
            return None
    
    def _download_file(self, url: str, destination: str) -> bool:
        """Descarga un archivo desde una URL."""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Descargado: {destination}")
            return True
        except requests.RequestException as e:
            logger.error(f"Error al descargar {url}: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula el hash SHA256 de un archivo."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except FileNotFoundError:
            return ""
    
    def update_component(self, component_name: str) -> bool:
        """Actualiza un componente específico."""
        if component_name not in self.config:
            logger.error(f"Componente {component_name} no encontrado en configuración")
            return False
        
        component_config = self.config[component_name]
        repo_url = component_config["source_url"]
        files_to_download = component_config["files"]
        
        logger.info(f"Actualizando {component_name}...")
        
        # Obtener información de la versión actual
        current_version = self._get_current_version(component_name)
        
        # Determinar si usar releases o commits
        use_releases = component_config.get("use_releases", True)
        
        if use_releases:
            latest_info = self._get_latest_release(repo_url)
            if not latest_info:
                logger.warning(f"No se encontraron releases para {component_name}, usando commits")
                use_releases = False
        
        if not use_releases:
            latest_info = self._get_latest_commit(repo_url)
        
        if not latest_info:
            logger.error(f"No se pudo obtener información de {component_name}")
            return False
        
        # Determinar la versión/hash actual
        if use_releases:
            latest_version = latest_info["tag_name"]
            current_hash = current_version.get("version") if current_version else None
        else:
            latest_version = latest_info["sha"][:8]  # Usar los primeros 8 caracteres del SHA
            current_hash = current_version.get("commit_hash") if current_version else None
        
        # Verificar si necesita actualización
        if current_hash == latest_version:
            logger.info(f"{component_name} ya está actualizado ({latest_version})")
            return True
        
        logger.info(f"Actualizando {component_name} de {current_hash or 'N/A'} a {latest_version}")
        
        # Descargar archivos
        updated_files = []
        for file_info in files_to_download:
            source_path = file_info["source"]
            dest_path = os.path.join(component_name, file_info["destination"])
            
            # Construir URL de descarga
            if use_releases:
                # Para releases, usar la URL del asset
                download_url = None
                for asset in latest_info.get("assets", []):
                    if asset["name"] == os.path.basename(source_path):
                        download_url = asset["browser_download_url"]
                        break
                
                if not download_url:
                    # Si no hay asset, usar raw URL
                    download_url = f"{repo_url}/raw/{latest_info['tag_name']}/{source_path}"
            else:
                # Para commits, usar raw URL
                download_url = f"{repo_url}/raw/{latest_info['sha']}/{source_path}"
            
            if self._download_file(download_url, dest_path):
                updated_files.append(dest_path)
            else:
                logger.error(f"Falló la descarga de {source_path}")
                return False
        
        # Guardar información de versión
        version_info = {
            "version": latest_version,
            "source_url": repo_url,
            "last_updated": datetime.now().isoformat(),
            "commit_hash" if not use_releases else "version": latest_version,
            "files": updated_files,
            "file_hashes": {f: self._calculate_file_hash(f) for f in updated_files}
        }
        
        self._save_version_info(component_name, version_info)
        logger.info(f"✅ {component_name} actualizado exitosamente a {latest_version}")
        return True
    
    def update_all_components(self) -> Dict[str, bool]:
        """Actualiza todos los componentes configurados."""
        results = {}
        for component_name in self.config.keys():
            results[component_name] = self.update_component(component_name)
        return results
    
    def check_for_updates(self) -> Dict[str, Dict]:
        """Verifica si hay actualizaciones disponibles sin descargar."""
        updates_available = {}
        
        for component_name in self.config.keys():
            component_config = self.config[component_name]
            repo_url = component_config["source_url"]
            current_version = self._get_current_version(component_name)
            
            use_releases = component_config.get("use_releases", True)
            
            if use_releases:
                latest_info = self._get_latest_release(repo_url)
                if not latest_info:
                    latest_info = self._get_latest_commit(repo_url)
                    use_releases = False
            else:
                latest_info = self._get_latest_commit(repo_url)
            
            if latest_info:
                if use_releases:
                    latest_version = latest_info["tag_name"]
                    current = current_version.get("version") if current_version else None
                else:
                    latest_version = latest_info["sha"][:8]
                    current = current_version.get("commit_hash") if current_version else None
                
                if current != latest_version:
                    updates_available[component_name] = {
                        "current": current or "N/A",
                        "latest": latest_version,
                        "url": repo_url
                    }
        
        return updates_available

def main():
    """Función principal del script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Actualizador de componentes de Lovelace")
    parser.add_argument("--check", action="store_true", help="Solo verificar actualizaciones")
    parser.add_argument("--component", type=str, help="Actualizar solo un componente específico")
    parser.add_argument("--config", type=str, default="components_config.json", 
                       help="Archivo de configuración")
    
    args = parser.parse_args()
    
    updater = ComponentUpdater(args.config)
    
    if args.check:
        updates = updater.check_for_updates()
        if updates:
            print("Actualizaciones disponibles:")
            for component, info in updates.items():
                print(f"  {component}: {info['current']} → {info['latest']}")
        else:
            print("Todos los componentes están actualizados")
    elif args.component:
        updater.update_component(args.component)
    else:
        results = updater.update_all_components()
        failed = [name for name, success in results.items() if not success]
        if failed:
            print(f"❌ Falló la actualización de: {', '.join(failed)}")
        else:
            print("✅ Todos los componentes actualizados exitosamente")

if __name__ == "__main__":
    main()