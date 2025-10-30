#!/usr/bin/env python3
"""
Simple script to generate basic PNG icons for the browser extension.
Creates blue square icons with white "L" text.
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL/Pillow not available. Install with: pip install Pillow")
    print("Attempting to create minimal icons without PIL...")

def create_icon_with_pil(size, filename):
    """Create icon using PIL/Pillow."""
    # Create blue background
    img = Image.new('RGB', (size, size), color='#0a66c2')
    draw = ImageDraw.Draw(img)

    # Calculate font size (roughly 60% of icon size)
    font_size = int(size * 0.6)

    # Try to use a system font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
        except:
            font = ImageFont.load_default()

    # Draw "L" in center
    text = "L"

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((size - text_width) // 2, (size - text_height) // 2 - bbox[1])

    draw.text(position, text, fill='white', font=font)

    # Save
    img.save(filename, 'PNG')
    print(f"✓ Created {filename} ({size}x{size})")

def create_minimal_icon(size, filename):
    """Create a very minimal icon without PIL (solid color with minimal header)."""
    # This creates a minimal valid PNG file (solid blue square)
    # Note: This is a simplified version and won't have the "L" text

    import struct
    import zlib

    def create_png_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = zlib.crc32(chunk) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', crc)

    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk (image header)
    ihdr_data = struct.pack('>IIBBBBB', size, size, 8, 2, 0, 0, 0)
    ihdr_chunk = create_png_chunk(b'IHDR', ihdr_data)

    # Create solid blue image data
    # RGB for #0a66c2 is (10, 102, 194)
    row = b'\x00' + (b'\x0a\x66\xc2' * size)  # Filter byte + pixels
    raw_data = row * size

    # Compress image data
    compressed_data = zlib.compress(raw_data, 9)
    idat_chunk = create_png_chunk(b'IDAT', compressed_data)

    # IEND chunk (image end)
    iend_chunk = create_png_chunk(b'IEND', b'')

    # Write PNG file
    with open(filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr_chunk)
        f.write(idat_chunk)
        f.write(iend_chunk)

    print(f"✓ Created {filename} ({size}x{size}) - solid blue square")

def main():
    print("Generating extension icons...")
    print()

    sizes = [(16, 'icon16.png'), (48, 'icon48.png'), (128, 'icon128.png')]

    for size, filename in sizes:
        if PIL_AVAILABLE:
            create_icon_with_pil(size, filename)
        else:
            create_minimal_icon(size, filename)

    print()
    if PIL_AVAILABLE:
        print("✓ All icons created successfully with text!")
    else:
        print("✓ Basic icons created (solid blue squares)")
        print("  For icons with 'L' text, install Pillow: pip install Pillow")
        print("  Then run this script again")
    print()
    print("Icons are ready for the browser extension!")

if __name__ == '__main__':
    main()
