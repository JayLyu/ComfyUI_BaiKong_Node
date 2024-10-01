from PIL import Image
import numpy as np
import os
import platform
import subprocess
import folder_paths
import time
from .functions_image import tensor2pil,pil2tensor

class BK_PrintImage:

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "trigger": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "printer_name": ("STRING", {"default": ""}),
                "output_folder": ("STRING", {"default": "prints"}),
                "filename_prefix": ("STRING", {"default": "print"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("PRINT_RESULT",)
    OUTPUT_NODE = False
    FUNCTION = "print_image"

    CATEGORY = "⭐️ Baikong/Image"
    DESCRIPTION = "(BETA) Send the input image to a printer for printing. Supports Windows and Mac systems."

    def print_image(self, image, trigger, printer_name="", output_folder="prints", filename_prefix="print"):
        if not trigger:
            return ("No print operation performed.",)

        # 保存临时文件
        preview = self.save_image("Preview", output_folder, image, "png", filename_prefix=filename_prefix, trigger=True)
        
        if not preview:
            return ("Failed to save temporary file.",)

        temp_filename = preview["ui"]["images"][0]["filename"]
        temp_path = preview["ui"]["images"][0]["subfolder"]
        full_path = os.path.join(temp_path, temp_filename)

        try:
            if platform.system() == "Windows":
                status = self.print_windows(full_path, printer_name)
            elif platform.system() == "Darwin":  # macOS
                status = self.print_mac(full_path, printer_name)
            else:
                return ("Unsupported operating system.",)
            
            if not printer_name:
                printer_name = "default printer"
            
            output_message = f"Temporary image {temp_filename} has been sent to printer {printer_name}. "
            output_message += f"File saved in {temp_path}. "
            output_message += f"Operating system: {platform.system()}. "
            output_message += f"Print status: {status}"
            
            return (output_message,)
        except Exception as e:
            return (f"Print failed: {str(e)}",)

    def save_image(self, mode, output_folder, image, file_format, output_path='', filename_prefix="print", trigger=False):
        if not trigger:
            return ()
        
        output_dir = folder_paths.get_output_directory()  
        out_folder = os.path.join(output_dir, output_folder)

        if output_path != '':
            if not os.path.exists(output_path):
                print(f"[Warning] BK Print Image: The input_path `{output_path}` does not exist")
                return ("",)
            out_path = output_path
        else:
            out_path = os.path.join(output_dir, out_folder)
        
        if mode == "Preview":
            out_path = folder_paths.temp_directory

        print(f"[Info] BK Print Image: Output path is `{out_path}`")
        
        counter = self.find_highest_numeric_value(out_path, filename_prefix) + 1
        
        output_image = image[0].cpu().numpy()
        img = Image.fromarray(np.clip(output_image * 255.0, 0, 255).astype(np.uint8))
        
        output_filename = f"{filename_prefix}_{counter:05}"
        img_params = {'png': {'compress_level': 4}}
        self.type = "output" if mode == "Save" else 'temp'

        resolved_image_path = os.path.join(out_path, f"{output_filename}.{file_format}")
        img.save(resolved_image_path, **img_params[file_format])
        print(f"[Info] BK Print Image: Saved to {output_filename}.{file_format}")
        out_filename = f"{output_filename}.{file_format}"
        preview = {"ui": {"images": [{"filename": out_filename,"subfolder": out_path,"type": self.type,}]}}
       
        return preview

    def find_highest_numeric_value(self, folder_path, prefix):
        highest = 0
        for filename in os.listdir(folder_path):
            if filename.startswith(prefix) and filename.endswith('.png'):
                try:
                    number = int(filename[len(prefix)+1:-4])
                    highest = max(highest, number)
                except ValueError:
                    pass
        return highest

    def print_windows(self, filename, printer_name):
        import win32print
        import win32ui
        from PIL import ImageWin

        if not printer_name:
            printer_name = win32print.GetDefaultPrinter()
        
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)
            
            hdc.StartDoc('ComfyUI Image Print')
            hdc.StartPage()
            
            dpi_x = hdc.GetDeviceCaps(88)
            dpi_y = hdc.GetDeviceCaps(90)
            
            width = int(8.5 * dpi_x)
            height = int(11 * dpi_y)
            
            image = Image.open(filename)
            image = image.resize((width, height), Image.LANCZOS)
            
            dib = ImageWin.Dib(image)
            
            dib.draw(hdc.GetHandleOutput(), (0, 0, width, height))
            
            hdc.EndPage()
            hdc.EndDoc()
            
            print(f"Image has been sent to printer: {printer_name}")
        
        finally:
            win32print.ClosePrinter(hprinter)

    def print_mac(self, filename, printer_name):
        # 构建 lpr 命令
        lpr_command = ["lpr"]
        if printer_name:
            lpr_command.extend(["-P", printer_name])
        lpr_command.append(filename)
        
        # 执行打印命令
        try:
            result = subprocess.run(lpr_command, capture_output=True, text=True, check=True)
            job_id = result.stdout.strip()  # lpr 通常会返回作业 ID
            status = self.check_print_job_status_mac(job_id)
            return status
        except subprocess.CalledProcessError as e:
            raise Exception(f"Print failed: {str(e)}")

    def check_print_job_status_mac(self, job_id, timeout=60):
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(["lpstat", "-l", job_id], capture_output=True, text=True, check=True)
                if "printing" in result.stdout.lower():
                    return "Printing started"
                elif "completed" in result.stdout.lower():
                    return "Printing completed"
            except subprocess.CalledProcessError:
                # 如果作业已经完成，lpstat 可能会返回错误
                return "Printing likely completed"
            time.sleep(1)
        return "Timeout: Unable to confirm print start"