"""
Legacy folder cleanup utility with safety mechanisms.
"""
import os
import shutil
import logging
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LegacyCleanup:
    """
    Manages the safe removal of legacy folders with rollback capability.
    """
    
    def __init__(self):
        self.legacy_folders = ["core", "indexing", "retriever", "evaluation"]
        self.backup_prefix = f"legacy_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.backup_created = False
    
    def create_backup(self) -> Dict[str, Any]:
        """Create backup of legacy folders before removal."""
        logger.info("Creating backup of legacy folders...")
        
        backup_info = {
            "backup_prefix": self.backup_prefix,
            "folders_backed_up": [],
            "backup_location": os.path.join(os.getcwd(), f"{self.backup_prefix}_folders"),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            backup_dir = backup_info["backup_location"]
            os.makedirs(backup_dir, exist_ok=True)
            
            for folder in self.legacy_folders:
                if os.path.exists(folder):
                    backup_path = os.path.join(backup_dir, folder)
                    shutil.copytree(folder, backup_path)
                    backup_info["folders_backed_up"].append(folder)
                    logger.info(f"Backed up {folder} to {backup_path}")
                else:
                    logger.warning(f"Folder {folder} does not exist, skipping backup")
            
            self.backup_created = True
            logger.info(f"Backup completed: {backup_info}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            raise
    
    def remove_legacy_folders(self, force: bool = False) -> Dict[str, Any]:
        """Remove legacy folders after backup."""
        if not force and not self.backup_created:
            raise ValueError("Backup must be created before removing legacy folders. Use create_backup() first.")
        
        logger.info("Removing legacy folders...")
        
        removal_info = {
            "folders_removed": [],
            "folders_not_found": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        for folder in self.legacy_folders:
            try:
                if os.path.exists(folder):
                    shutil.rmtree(folder)
                    removal_info["folders_removed"].append(folder)
                    logger.info(f"Removed folder: {folder}")
                else:
                    removal_info["folders_not_found"].append(folder)
                    logger.info(f"Folder not found (already removed): {folder}")
            except Exception as e:
                error_msg = f"Failed to remove {folder}: {e}"
                removal_info["errors"].append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Legacy folder removal completed: {removal_info}")
        return removal_info
    
    def restore_from_backup(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Restore legacy folders from backup."""
        logger.info("Restoring legacy folders from backup...")
        
        restore_info = {
            "folders_restored": [],
            "errors": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            backup_dir = backup_info["backup_location"]
            
            if not os.path.exists(backup_dir):
                raise ValueError(f"Backup directory not found: {backup_dir}")
            
            for folder in backup_info["folders_backed_up"]:
                try:
                    backup_path = os.path.join(backup_dir, folder)
                    if os.path.exists(backup_path):
                        shutil.copytree(backup_path, folder)
                        restore_info["folders_restored"].append(folder)
                        logger.info(f"Restored folder: {folder}")
                    else:
                        error_msg = f"Backup not found for folder: {folder}"
                        restore_info["errors"].append(error_msg)
                        logger.error(error_msg)
                except Exception as e:
                    error_msg = f"Failed to restore {folder}: {e}"
                    restore_info["errors"].append(error_msg)
                    logger.error(error_msg)
            
            logger.info(f"Restore completed: {restore_info}")
            return restore_info
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
    
    def get_legacy_folder_status(self) -> Dict[str, Any]:
        """Get current status of legacy folders."""
        status = {
            "folders_exist": [],
            "folders_missing": [],
            "backup_created": self.backup_created,
            "backup_prefix": self.backup_prefix if self.backup_created else None,
            "timestamp": datetime.now().isoformat()
        }
        
        for folder in self.legacy_folders:
            if os.path.exists(folder):
                status["folders_exist"].append(folder)
            else:
                status["folders_missing"].append(folder)
        
        return status
    
    def cleanup_backup(self, backup_info: Dict[str, Any]) -> Dict[str, Any]:
        """Remove backup after successful cleanup."""
        logger.info("Cleaning up backup...")
        
        cleanup_info = {
            "backup_removed": False,
            "error": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            backup_dir = backup_info["backup_location"]
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
                cleanup_info["backup_removed"] = True
                logger.info(f"Backup removed: {backup_dir}")
            else:
                logger.warning(f"Backup directory not found: {backup_dir}")
                
        except Exception as e:
            cleanup_info["error"] = str(e)
            logger.error(f"Backup cleanup failed: {e}")
        
        return cleanup_info

