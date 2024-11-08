import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import subprocess
import re
import requests
import json
#pdf zimbirtilari
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

def export_texts_to_pdf(texts, output_filename):
    # PDF dosyasını oluştur
    pdf = SimpleDocTemplate(output_filename, pagesize=letter)
    elements = []

    # Türkçe karakter desteği için fontu ekleyin
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))  # Font dosyasının yolu
    styles = getSampleStyleSheet()
    
    # Normal stil için fontu ayarlayın
    normal_style = ParagraphStyle(
        name='Normal',
        fontName='DejaVuSans',
        fontSize=12,
        leading=15,
    )

    for text in texts:
        # Metni Paragraph ile oluştur ve PDF'ye ekle
        paragraph = Paragraph(text, normal_style)
        elements.append(paragraph)
        elements.append(Spacer(1, 12))  # Her metin arasında boşluk bırak

    # PDF dosyasını oluştur ve kaydet
    pdf.build(elements)	
    
class QuestionGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Model Tabanlı Soru Üretici")
        self.root.geometry("700x700")

        # Model Seçimi Bölümü
        model_frame = ttk.LabelFrame(root, text="Modeller")
        model_frame.pack(fill="x", padx=10, pady=5)

        self.models = self.get_models()
        self.selected_model = tk.StringVar()
        if self.models:
            self.selected_model.set(self.models[0])
        else:
            self.selected_model.set("Model bulunamadı")

        self.model_dropdown = ttk.OptionMenu(model_frame, self.selected_model, *self.models)
        self.model_dropdown.pack(padx=10, pady=10)

        # Alan Seçimi Bölümü
        field_frame = ttk.LabelFrame(root, text="Alan Seçimi")
        field_frame.pack(fill="x", padx=10, pady=5)

        self.selected_field = tk.StringVar()
        fields = ["Dijital Dönüşüm", "Python Kodlama", "Power BI", "Ağ ve Güvenlik","Veritabanı","Web Uygulamaları"]
        self.selected_field.set(fields[0])

        field_dropdown = ttk.OptionMenu(field_frame, self.selected_field, *fields)
        field_dropdown.pack(padx=10, pady=10)
        
        #adet
        pcs_frame = ttk.LabelFrame(root, text="Soru Sayısı")
        pcs_frame.pack(fill="x", padx=10, pady=5)
        self.selected_pcs = tk.StringVar()
        # ~ pcs = ['bir','iki','üç','dört','beş','altı','yedi','sekiz','dokuz','on']
        pcs = [1,2,3,4,5,6,7,8,9,10]
        self.selected_pcs.set(pcs[0])
        pcs_dropdown = ttk.OptionMenu(pcs_frame, self.selected_pcs, *pcs)
        pcs_dropdown.pack(padx=10, pady=10)
        

        # Soru Üretme Butonu
        generate_button = ttk.Button(root, text="Soruları Üret", command=self.start_generation)
        generate_button.pack(pady=10)
        
        # ~ # PDF Kaydet Butonu
        # ~ generate_button = ttk.Button(root, text="PDF Kaydet", command=self.export_texts_to_pdf(questions, output_filename))
        # ~ generate_button.pack(pady=10)

        # Yükleme Çubuğu ve Süre
        progress_frame = ttk.Frame(root)
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress = ttk.Progressbar(progress_frame, orient='horizontal', mode='determinate')
        self.progress.pack(fill="x", padx=10, pady=5)

        self.time_label = ttk.Label(progress_frame, text="Geçen Süre: 0s")
        self.time_label.pack(pady=5)

        # Çıktı Metin Kutusu
        output_frame = ttk.LabelFrame(root, text="Üretilen Sorular")
        output_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.output_text = tk.Text(output_frame, wrap="word")
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def get_models(self):
        try:
            # "ollama list" komutunu çalıştır ve çıktısını al
            result = subprocess.run(['ollama', 'list'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            output = result.stdout
            # Çıktıyı parse et
            models = self.parse_ollama_list(output)
            if not models:
                messagebox.showwarning("Uyarı", "Hiç model bulunamadı.")
            return models
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Hata", f"Ollama komutu çalıştırılamadı:\n{e.stderr}")
            return []
        except FileNotFoundError:
            messagebox.showerror("Hata", "Ollama komutu bulunamadı. Lütfen Ollama'nın kurulu ve PATH'e ekli olduğundan emin olun.")
            return []

    def parse_ollama_list(self, output):
        models = []
        lines = output.strip().split('\n')
        # Başlık satırını atla
        for line in lines[1:]:
            # Satır formatı:
            # NAME                                        ID              SIZE      MODIFIED     
            # Örneğin:
            # llama3.2:latest                             a80c4f17acd5    2.0 GB    6 days ago      
            # Modellerin isimlerini al
            match = re.match(r'^(\S+)', line)
            if match:
                model_name = match.group(1)
                models.append(model_name)
        return models

    def start_generation(self):
        if not self.models:
            messagebox.showwarning("Uyarı", "Hiç model bulunamadı.")
            return

        selected_model = self.selected_model.get()
        selected_field = self.selected_field.get()
        selected_pcs = self.selected_pcs.get()

        # Soru üretme işlemini ayrı bir thread'de başlat
        threading.Thread(target=self.generate_questions, args=(selected_model, selected_field, selected_pcs), daemon=True).start()


        
    def generate_questions(self, model, field, pcs):
        # Progress bar'ı determinate moda al ve sıfırla
        self.progress.config(mode='determinate', maximum=100, value=0)
        self.time_label.config(text="Geçen Süre: 0s")
        self.output_text.delete(1.0, tk.END)

        start_time = time.time()

        try:
            # Soru üretme işlemi için API çağrısı yap
            questions = self.create_questions_with_ollama(model, field, pcs)

            elapsed = int(time.time() - start_time)
            self.time_label.config(text=f"Geçen Süre: {elapsed}s")

            # Progress bar'ı tamamlanmış olarak ayarla
            self.progress['value'] = 100
            #soruları pdf kaydet
            export_texts_to_pdf(questions, './test.pdf')
            # Soruları metin kutusuna ekle
            for q in questions:
                self.output_text.insert(tk.END, f"- {q}\n")

        except Exception as e:
            # Hata durumunda progress bar'ı durdur ve hata mesajı göster
            self.progress['value'] = 0
            messagebox.showerror("Hata", f"Soru üretme sırasında bir hata oluştu:\n{e}")

    def create_questions_with_ollama(self, model, field, pcs):
        """
        Ollama API kullanarak seçilen model ve alana göre iki soru üretir.

        Args:
            model (str): Kullanılacak modelin adı.
            field (str): Soru üretilecek alan.

        Returns:
            list: Üretilen soruların listesi.

        Raises:
            Exception: API çağrısı başarısız olursa.
        """
        # Ollama API endpoint'i
        api_url = "http://localhost:11434/api/generate"  # Doğru endpoint

        # API için gerekli payload
        # Prompt'u daha net yapmak için her sorunun ayrı satırda olmasını talep ediyoruz
        payload = {
            "model": model,
            "prompt": f"Lütfen {field} alanında {pcs} adet özgün soru üretiniz. Her bir soruyu '1.' ve '2.' ile numaralandırarak ayrı satırlarda yazınız."
        }
        # ~ print(payload)
        headers = {
            "Content-Type": "application/json"
            # Gerekli ise yetkilendirme başlıkları ekleyin
        }

        # Streaming yanıt için stream=True
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), stream=True, timeout=60)

        # Yanıtı yazdırarak kontrol edin
        print("API Response Status Code:", response.status_code)
        # print("API Response Text:", response.text)  # Bu, çok fazla çıktı verebilir

        if response.status_code != 200:
            raise Exception(f"API çağrısı başarısız oldu. Status Code: {response.status_code}, Mesaj: {response.text}")

        generated_text = ""
        questions = []

        try:
            for line in response.iter_lines():
                if line:
                    try:
                        json_obj = json.loads(line.decode('utf-8'))
                        response_text = json_obj.get("response", "")
                        done = json_obj.get("done", False)
                        generated_text += response_text

                        # Debug: Her bir parça ekrana yazdırılabilir
                        print(f"Received chunk: {response_text}")

                        if done:
                            break
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                        continue

            if not generated_text:
                raise Exception("API'den geçerli bir yanıt alınamadı.")

            # Soruları ayırmak için numaralandırmayı kullan
            # Örneğin: "1. Soru?\n2. Soru?"
            # Regex ile "1. " ve "2. " başlangıçlarını bulup ayırabiliriz
            # ~ pattern = r'1\.\s*(.*?)\s*2\.\s*(.*)'
            # ~ match = re.search(pattern, generated_text, re.DOTALL)
            
            pattern = r'\d+\.\s*"(.*?)"'
            # ~ Hquestions = re.findall(Hpattern, generated_text)
            match = re.findall(pattern, generated_text)
            
            if match:
                # ~ question1 = match.group(1).strip()
                # ~ question2 = match.group(2).strip()
                # ~ questions = [question1, question2]
                questions=match
            else:
                # Eğer numaralandırma yoksa, satır satır ayırmayı deneyin
                questions = [q.strip() for q in generated_text.split('\n') if q.strip()]
                if len(questions) < 2:
                    raise Exception("İki soru alınamadı. API'nin yanıt formatını kontrol edin.")

            # ~ return questions[:2]  # İlk iki soruyu döndür
            return questions[:int(pcs)]  # İlk iki soruyu döndür

        except requests.exceptions.RequestException as e:
            raise Exception(f"API çağrısı sırasında bir hata oluştu: {e}")
        except Exception as e:
            raise Exception(f"Yanıt işleme sırasında bir hata oluştu: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionGeneratorApp(root)
    root.mainloop()
