import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
import concurrent.futures

def download_and_convert_image(img_url, save_folder, index):
    """下载并转换 WebP 图片为 JPG 格式"""
    try:
        # 补全相对路径为绝对 URL
        if not img_url.startswith(('http:', 'https:')):
            img_url = urljoin(base_url, img_url)
            
        response = requests.get(img_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        
        # 识别文件名和扩展名
        filename = f"image_{index}.jpg"  # 强制保存为 JPG
        save_path = os.path.join(save_folder, filename)
        
        # 检测是否为 WebP 并转换
        if img_url.endswith('.webp') or response.headers.get('Content-Type', '').lower() == 'image/webp':
            img = Image.open(BytesIO(response.content))
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(save_path, 'JPEG')
            return f"转换成功: {save_path}"
        else:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return f"下载成功: {save_path}"
            
    except Exception as e:
        return f"失败 {img_url}: {str(e)}"

def download_fandom_images(url, folder='fandom_images', max_workers=5):
    """主下载函数，支持并发处理"""
    global base_url
    base_url = url
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    try:
        # 模拟浏览器请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tags = soup.find_all('img', src=True)
        
        if not img_tags:
            return "未找到图片，请检查页面结构"
        
        # 并发下载处理
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, img in enumerate(img_tags):
                img_url = img['src'].split('?')[0]  # 清除URL参数
                if not img_url: continue
                futures.append(executor.submit(download_and_convert_image, img_url, folder, i))
                
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        return "\n".join(results)
        
    except Exception as e:
        return f"致命错误: {str(e)}"

if __name__ == "__main__":
    # 使用示例
    fandom_url = "https://sky-children-of-the-light.fandom.com/wiki/World_Maps"  # 替换为目标页面
    result = download_fandom_images(fandom_url)
    print(result)

#https://sky-children-of-the-light.fandom.com/wiki/World_Maps
