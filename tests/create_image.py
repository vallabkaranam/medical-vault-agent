from PIL import Image, ImageDraw, ImageFont
import os

def create_test_image(filename="test_record.jpg"):
    # Create a white image
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)
    
    # Add some text simulating a vaccine record
    text = """
    OFFICIAL VACCINATION RECORD
    Name: John Doe
    DOB: 01/01/1980
    
    VACCINES:
    1. MMR (Measles, Mumps, Rubella)
       Date: 2024-01-15
       Lot: Merck-123
       Provider: CVS Pharmacy
       
    2. Tdap (Tetanus, Diphtheria, Pertussis)
       Date: 2023-11-20
       Lot: GSK-456
       Provider: Walgreens
    """
    
    # Use default font
    d.text((10, 10), text, fill=(0, 0, 0))
    
    # Save
    img.save(filename)
    print(f"Created test image: {filename}")

if __name__ == "__main__":
    create_test_image()
