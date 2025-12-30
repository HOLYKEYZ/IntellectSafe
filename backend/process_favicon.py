from PIL import Image, ImageOps

def process_favicon(input_path, output_path):
    print(f"Processing {input_path}...")
    try:
        img = Image.open(input_path)
        img = img.convert("RGBA")
        
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img_with_bg = Image.alpha_composite(bg, img)
        img_with_bg = img_with_bg.convert("RGB")

        inverted = ImageOps.invert(img_with_bg)
        bbox = inverted.getbbox()
        
        if bbox:
            cropped = img_with_bg.crop(bbox)
            print(f"Cropped to {bbox}")
            
            w, h = cropped.size
            max_dim = max(w, h)
            final_img = Image.new("RGB", (max_dim, max_dim), (255, 255, 255))
            
            offset_x = (max_dim - w) // 2
            offset_y = (max_dim - h) // 2
            offset_x = (max_dim - w) // 2
            offset_y = (max_dim - h) // 2
            final_img.paste(cropped, (offset_x, offset_y))
            
            final_img.save(output_path, "PNG")
            print(f"Saved optimized favicon to {output_path}")
        else:
            print("Could not find bounding box, saving original")
            img_with_bg.save(output_path, "PNG")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    input_logo = r"C:\Users\USER\.gemini\antigravity\brain\9aab4c06-7ede-4561-a14c-28da23e5c829\intellectsafe_clean_is_black_1767113000634.png"
    output_favicon = r"c:\Users\USER\Desktop\cursor file\AI-safety\frontend\public\favicon.png"
    
    process_favicon(input_logo, output_favicon)
