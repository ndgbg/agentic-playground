# Multi-Modal Agent

Process images and text together using vision-language models. Analyze images, answer questions about visual content, and combine text and image understanding.

## Overview

This agent uses Claude 3's vision capabilities to understand both text and images. Ask questions about images, get descriptions, detect objects, analyze scenes, and more.

## Quick Start

```bash
cd advanced-patterns/multimodal-agent
pip install -r requirements.txt
python multimodal_agent.py
```

**Output:**
```
Multi-Modal Agent
============================================================

Image: office.jpg
Query: What do you see in this image?

Response: I see an office workspace with:
- A person sitting at a desk
- A laptop computer open with code on the screen
- Two monitors in the background
- A coffee mug on the desk
- Natural lighting from a window
- Books on a shelf

The environment appears to be a modern home office setup.
============================================================

Image: chart.png
Query: What does this chart show?

Response: This bar chart shows quarterly revenue growth:
- Q1: $2.5M
- Q2: $3.1M (24% increase)
- Q3: $3.8M (23% increase)
- Q4: $4.2M (11% increase)

Overall trend shows consistent growth throughout the year,
with strongest growth in Q2 and Q3.
============================================================
```

## Capabilities

### Image Analysis
- Scene description
- Object detection
- Text extraction (OCR)
- Color analysis
- Composition analysis

### Visual Q&A
- Answer questions about image content
- Identify objects and people
- Describe relationships
- Explain context

### Document Understanding
- Extract text from documents
- Analyze charts and graphs
- Read tables and forms
- Process receipts and invoices

### Accessibility
- Generate alt text for images
- Describe visual content for screen readers
- Explain diagrams and illustrations

## Available Tools

### analyze_image()
Analyze image and answer questions:
```python
analyze_image(
    image_path="photo.jpg",
    query="What objects are in this image?"
)
```

### extract_text()
Extract text from images (OCR):
```python
extract_text(image_path="document.png")
# Returns: "Invoice #12345\nDate: 2026-01-26\nTotal: $150.00"
```

### describe_scene()
Get detailed scene description:
```python
describe_scene(image_path="landscape.jpg")
# Returns: "A mountain landscape at sunset with..."
```

### compare_images()
Compare multiple images:
```python
compare_images(
    image_paths=["before.jpg", "after.jpg"],
    query="What changed between these images?"
)
```

## Example Use Cases

### Product Catalog
```python
# Analyze product images
response = analyze_image(
    "product.jpg",
    "Describe this product and its features"
)
# Use for auto-generating product descriptions
```

### Quality Control
```python
# Inspect manufacturing defects
response = analyze_image(
    "part.jpg",
    "Are there any defects or damage visible?"
)
# Flag items for review
```

### Document Processing
```python
# Extract invoice data
response = analyze_image(
    "invoice.pdf",
    "Extract invoice number, date, and total amount"
)
# Parse into structured data
```

### Content Moderation
```python
# Check image content
response = analyze_image(
    "user_upload.jpg",
    "Does this image contain inappropriate content?"
)
# Approve or reject uploads
```

## Customization

### Add Image Preprocessing

```python
from PIL import Image, ImageEnhance

@tool
def preprocess_image(image_path: str) -> str:
    """Enhance image before analysis"""
    img = Image.open(image_path)
    
    # Resize if too large
    if img.width > 2000:
        ratio = 2000 / img.width
        img = img.resize((2000, int(img.height * ratio)))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Save processed image
    processed_path = "/tmp/processed.jpg"
    img.save(processed_path)
    return processed_path
```

### Add Object Detection

```python
import cv2

@tool
def detect_objects(image_path: str) -> list:
    """Detect objects using OpenCV"""
    img = cv2.imread(image_path)
    
    # Load pre-trained model
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    
    # Detect objects
    blob = cv2.dnn.blobFromImage(img, 1/255, (416, 416))
    net.setInput(blob)
    outputs = net.forward()
    
    # Parse detections
    objects = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                objects.append({
                    "class": class_names[class_id],
                    "confidence": float(confidence)
                })
    
    return objects
```

### Add Face Detection

```python
import face_recognition

@tool
def detect_faces(image_path: str) -> dict:
    """Detect and count faces"""
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    
    return {
        "face_count": len(face_locations),
        "locations": face_locations
    }
```

## Integration Examples

### Process S3 Images

```python
import boto3

s3 = boto3.client('s3')

def process_s3_image(bucket: str, key: str):
    # Download image
    s3.download_file(bucket, key, '/tmp/image.jpg')
    
    # Analyze
    response = analyze_image('/tmp/image.jpg', "Describe this image")
    
    # Store results
    s3.put_object(
        Bucket=bucket,
        Key=f"analysis/{key}.json",
        Body=json.dumps(response)
    )
```

### Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

def process_images_batch(image_paths: list, query: str):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(analyze_image, path, query)
            for path in image_paths
        ]
        results = [f.result() for f in futures]
    return results
```

### Real-Time Camera Feed

```python
import cv2

def process_camera_feed():
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Save frame
        cv2.imwrite('/tmp/frame.jpg', frame)
        
        # Analyze every 30 frames
        if cap.get(cv2.CAP_PROP_POS_FRAMES) % 30 == 0:
            response = analyze_image('/tmp/frame.jpg', "What's happening?")
            print(response)
        
        cv2.imshow('Feed', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
```

## Deploy to Production

### API Endpoint

```python
from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze_endpoint():
    # Get image from request
    image_data = request.json["image"]  # base64 encoded
    query = request.json["query"]
    
    # Decode and save
    image_bytes = base64.b64decode(image_data)
    with open('/tmp/upload.jpg', 'wb') as f:
        f.write(image_bytes)
    
    # Analyze
    response = analyze_image('/tmp/upload.jpg', query)
    
    return jsonify({"response": response})
```

### Lambda Function

```python
import json
import boto3

def lambda_handler(event, context):
    # Get image from S3
    bucket = event['bucket']
    key = event['key']
    
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, '/tmp/image.jpg')
    
    # Analyze
    response = analyze_image('/tmp/image.jpg', event['query'])
    
    return {
        'statusCode': 200,
        'body': json.dumps({'response': response})
    }
```

## Use Cases

### E-Commerce
- Auto-generate product descriptions
- Categorize products from images
- Detect product defects
- Verify product authenticity

### Healthcare
- Analyze medical images
- Detect anomalies in scans
- Extract data from forms
- Assist with diagnostics

### Real Estate
- Generate property descriptions
- Analyze room layouts
- Detect property features
- Compare before/after renovations

### Manufacturing
- Quality control inspection
- Defect detection
- Assembly verification
- Safety compliance checks

### Media & Entertainment
- Content moderation
- Auto-tagging images
- Scene detection
- Accessibility descriptions

## Best Practices

### Image Quality
```python
# Ensure good image quality
- Resolution: 1024x1024 or higher
- Format: JPEG or PNG
- Lighting: Well-lit, clear images
- Focus: Sharp, not blurry
```

### Prompt Engineering
```python
# Be specific in queries
❌ "What is this?"
✅ "Identify all objects in this image and their locations"

❌ "Describe"
✅ "Describe the scene, including people, objects, and activities"
```

### Error Handling
```python
def safe_analyze(image_path: str, query: str):
    try:
        # Check file exists
        if not os.path.exists(image_path):
            return "Error: Image file not found"
        
        # Check file size
        if os.path.getsize(image_path) > 5 * 1024 * 1024:  # 5MB
            return "Error: Image too large"
        
        # Analyze
        return analyze_image(image_path, query)
    
    except Exception as e:
        return f"Error: {str(e)}"
```

## Troubleshooting

**Poor Analysis Quality**
- Use higher resolution images
- Ensure good lighting
- Crop to relevant area
- Try different prompts

**Slow Processing**
- Resize large images
- Use batch processing
- Cache common queries
- Optimize image format

**Incorrect Results**
- Be more specific in queries
- Provide context in prompt
- Use multiple queries
- Verify image quality

## Next Steps

1. Test with your images
2. Tune prompts for your use case
3. Add preprocessing pipeline
4. Integrate with your application
5. Deploy to production
