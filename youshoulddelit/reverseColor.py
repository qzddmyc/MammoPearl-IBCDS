from PIL import Image
import os

def invert_image_colors():
    # 获取用户输入的图片路径
    img_path = input("请输入图片相对于当前目录的路径：").strip()
    
    # 检查路径是否存在
    if not os.path.exists(img_path):
        print("错误：指定的图片路径不存在！")
        return
    
    try:
        # 打开图片
        with Image.open(img_path) as img:
            # 获取图片信息
            width, height = img.size
            mode = img.mode
            pixels = img.load()  # 获取像素访问对象
            
            # 遍历每个像素进行反色处理
            for i in range(width):
                for j in range(height):
                    pixel = pixels[i, j]
                    
                    # 根据不同图像模式处理反色
                    if mode == 'RGB':
                        r, g, b = pixel
                        inverted_pixel = (255 - r, 255 - g, 255 - b)
                    elif mode == 'RGBA':
                        r, g, b, a = pixel
                        inverted_pixel = (255 - r, 255 - g, 255 - b, a)  # 保留透明度
                    elif mode == 'L':  # 灰度图
                        inverted_pixel = (255 - pixel[0],)
                    else:
                        raise ValueError(f"不支持的图片模式：{mode}")
                    
                    pixels[i, j] = inverted_pixel
            
            # 构建保存路径（在原文件名后添加"_inverted"）
            dir_name = os.path.dirname(img_path)
            base_name = os.path.basename(img_path)
            file_name, ext = os.path.splitext(base_name)
            new_file_name = f"{file_name}_inverted{ext}"
            new_path = os.path.join(dir_name, new_file_name)
            
            # 保存反色后的图片
            img.save(new_path)
            print(f"反色处理完成，图片已保存至：{new_path}")
            
    except Exception as e:
        print(f"处理图片时发生错误：{str(e)}")

if __name__ == "__main__":
    invert_image_colors()