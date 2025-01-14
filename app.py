# palm_disease_app_mobilevit.py

import streamlit as st
from PIL import Image
import torch
import timm
import numpy as np
from torchvision import transforms
import os

# ##############
# تهيئة النموذج
# ##############
@st.cache_resource
def load_model(model_path, num_labels):
    """
    تحميل نموذج MobileViT المدرب مسبقًا.
    
    Parameters:
        model_path (str): مسار ملف النموذج .pth
        num_labels (int): عدد الفئات

    Returns:
        model: نموذج MobileViT مُحمّل
    """
    model = timm.create_model('mobilevit_xxs', pretrained=False, num_classes=num_labels)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

# تعريف أسماء الفئات وخطط العلاج
CLASS_NAMES = [
    'نقص البوتاسيوم',
    'نقص المنغنيز',
    'نقص المغنيسيوم',
    'الحرق الأسود',
    'بقع الأوراق',
    'ذبول الفيوزاريوم',
    'لفحة السعف',
    'حشرة بلانشارد القشرية',
    'عينة سليمة'
]

ADVICE_DICT = {
    'نقص البوتاسيوم': 'استخدام أسمدة تحتوي على نسبة عالية من البوتاسيوم (مثل سلفات البوتاسيوم) وتطبيقها بانتظام. تحسين تصريف التربة لضمان عدم فقدان العناصر الغذائية.',
    'نقص المنغنيز': 'تحسين التربة باستخدام أسمدة تحتوي على المنغنيز مثل سلفات المنغنيز. تعديل مستوى الحموضة في التربة (pH) لجعل العناصر الغذائية متاحة للنبات.',
    'نقص المغنيسيوم': 'إضافة أسمدة تحتوي على المغنيسيوم مثل كبريتات المغنيسيوم. التأكد من توازن العناصر الغذائية في التربة.',
    'الحرق الأسود': 'استخدام مبيدات الفطريات المناسبة مثل تلك التي تحتوي على المانكوزيب أو الكاربندازيم. إزالة الأوراق المصابة لتقليل انتشار العدوى.',
    'بقع الأوراق': 'تطبيق مبيدات الفطريات مثل تلك التي تحتوي على الكلوروثالونيل. تجنب الري الزائد وضمان التهوية الجيدة بين الأشجار.',
    'ذبول الفيوزاريوم': 'إزالة وتدمير النباتات المصابة. استخدام مبيدات فطريات فعالة مثل تلك التي تحتوي على الثيوفانات-ميثيل. تحسين التصريف لمنع انتشار العدوى.',
    'لفحة السعف': 'رش الأشجار بمبيدات الفطريات المناسبة. تقليم الأجزاء المصابة لتحسين تهوية الشجرة.',
    'حشرة بلانشارد القشرية': 'استخدام المبيدات الحشرية المناسبة مثل الزيوت المعدنية أو الكلوربيريفوس. مراقبة الأشجار بانتظام للسيطرة على تفشي الآفات.',
    'عينة سليمة': 'الحفاظ على ممارسات زراعية جيدة تشمل الري والتسميد المنتظمين، والتأكد من التصريف الجيد، ومراقبة ظهور أي أعراض على الأشجار بانتظام.'
}

# تحميل النموذج
MODEL_PATH = 'https://github.com/atwahsz/palm_tree_app/raw/refs/heads/main/best_mobilevit_palm_disease.pth'  # تأكد من مسار النموذج الصحيح
NUM_LABELS = len(CLASS_NAMES)

# تحقق من وجود النموذج
if not os.path.exists(MODEL_PATH):
    st.error(f"لم يتم العثور على النموذج في المسار التالي: {MODEL_PATH}. يرجى التأكد من وجود ملف النموذج.")
    st.stop()

model = load_model(MODEL_PATH, NUM_LABELS)

# ##############
# تعريف الدوال
# ##############
def preprocess_image(image):
    """
    معالجة الصورة المدخلة لتكون مناسبة للنموذج MobileViT.
    
    Parameters:
        image (PIL.Image): الصورة المدخلة
    
    Returns:
        torch.Tensor: الصورة المعالجة
    """
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],  # متوسط ImageNet
                             std=[0.229, 0.224, 0.225])   # انحراف ImageNet
    ])
    return preprocess(image).unsqueeze(0)  # إضافة بعد الدفعة

def predict(image, model, class_names):
    """
    إجراء التنبؤ بالفئة بناءً على الصورة المدخلة.
    
    Parameters:
        image (PIL.Image): الصورة المدخلة
        model: نموذج MobileViT المُحمّل
        class_names (list): قائمة بأسماء الفئات
    
    Returns:
        predicted_class (str): الفئة المتوقعة
        confidence (float): درجة الثقة
    """
    input_tensor = preprocess_image(image)
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_class = torch.max(probabilities, dim=1)
    return class_names[predicted_class.item()], confidence.item()

def get_advice(class_name):
    """
    الحصول على خطة العلاج بناءً على الفئة المتوقعة.
    
    Parameters:
        class_name (str): اسم الفئة
    
    Returns:
        str: خطة العلاج
    """
    return ADVICE_DICT.get(class_name, 'لا توجد نصيحة متاحة لهذه الفئة.')

# ##############
# واجهة التطبيق
# ##############
st.set_page_config(page_title="📷 تشخيص أمراض أشجار النخيل", layout="centered")

st.title("📷 تطبيق تشخيص أمراض أشجار النخيل")

st.write("""
    هذا التطبيق يستخدم نموذج تعلم عميق لتشخيص أمراض أشجار النخيل من خلال صورة يتم تحميلها.
    يرجى التقاط صورة واضحة لأوراق النخيل وتحميلها أدناه.
""")

# تحميل الصورة
uploaded_file = st.file_uploader("اختر صورة لورقة النخيل", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert('RGB')
    st.image(image, caption='الصورة المحملة', use_column_width=True)
    
    if st.button('🔍 تشخيص'):
        with st.spinner('جارٍ التشخيص...'):
            predicted_class, confidence = predict(image, model, CLASS_NAMES)
            st.success(f"✅ **التشخيص:** {predicted_class}")
            st.info(f"📊 **درجة الثقة:** {confidence*100:.2f}%")
            
            advice = get_advice(predicted_class)
            st.write("### 📝 **خطة العلاج الموصى بها:**")
            st.write(advice)
else:
    st.write("يرجى تحميل صورة لبدء عملية التشخيص.")

# ##############
# ملاحظات إضافية
# ##############
st.markdown("""
---
**ملاحظة:** تأكد من أن النموذج `mobilevit_palm_disease_final.pth` موجود في المجلد المحدد (`model_outputs/`) أو قم بتعديل المسار في المتغير `MODEL_PATH` وفقًا لذلك.
""")
