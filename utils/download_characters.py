import os
import requests
import yaml
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterDownloader:
    def __init__(self, target_dir: str = "characters"):
        self.target_dir = target_dir
        self._ensure_target_dir()

    def _ensure_target_dir(self):
        """确保目标目录存在"""
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

    def download_from_github(self, repo_url: str, branch: str = "main"):
        """
        从GitHub仓库下载角色文件
        
        Args:
            repo_url: GitHub仓库URL (例如: https://github.com/username/repo)
            branch: 分支名称 (默认: main)
        """
        try:
            # 从URL中提取用户名和仓库名
            parts = repo_url.strip('/').split('/')
            if len(parts) < 2:
                raise ValueError("Invalid GitHub repository URL")
            
            username = parts[-2]
            repo_name = parts[-1]
            
            # 构建API URL
            api_url = f"https://api.github.com/repos/{username}/{repo_name}/contents/characters"
            
            # 获取characters目录内容
            response = requests.get(api_url)
            response.raise_for_status()
            
            files = response.json()
            if not isinstance(files, list):
                raise ValueError("Expected a list of files from GitHub API")
            
            # 下载每个YAML文件
            for file in files:
                if file['name'].endswith('.yaml'):
                    self._download_file(file['download_url'])
            
            logger.info(f"Successfully downloaded characters from {repo_url}")
            
        except Exception as e:
            logger.error(f"Error downloading characters: {str(e)}")
            raise

    def _download_file(self, download_url: str):
        """下载单个文件"""
        try:
            response = requests.get(download_url)
            response.raise_for_status()
            
            # 获取文件名
            filename = os.path.basename(download_url)
            filepath = os.path.join(self.target_dir, filename)
            
            # 检查文件是否已存在
            if os.path.exists(filepath):
                # 如果文件已存在，添加数字后缀
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    new_filename = f"{base}_{counter}{ext}"
                    filepath = os.path.join(self.target_dir, new_filename)
                    counter += 1
            
            # 保存文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            logger.info(f"Downloaded: {filename}")
            
        except Exception as e:
            logger.error(f"Error downloading file {download_url}: {str(e)}")
            raise

def main():
    # 创建下载器实例
    downloader = CharacterDownloader()
    
    # 从指定的GitHub仓库下载角色
    repo_url = "https://github.com/venetanji/polyu-storyworld"
    try:
        downloader.download_from_github(repo_url)
        print("Character download completed successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 