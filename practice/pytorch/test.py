from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from torchvision.models import efficientnet_v2_s
from torchvision import transforms
from PIL import Image
import torch
from io import BytesIO

app = FastAPI()

model = efficientnet_v2_s()
model.load_state_dict(torch.load("efficientnetv2_model.pth", map_location="cpu"))
model.eval()


transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], 
                         [0.229, 0.224, 0.225])
])

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(tensor)
            predicted_class = torch.argmax(outputs, dim=1).item()

        return {"predicted_class_index": predicted_class}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
