```python
import re
import nltk
from nltk.corpus import stopwords

# Download stopwords jika belum ada
try:
    nltk.download('stopwords', quiet=True)
except:
    pass

def clean_text(text):
    """
    Membersihkan teks dari karakter khusus, mengubah ke lowercase, dll
    
    Args:
        text (str): Teks yang akan dibersihkan
    
    Returns:
        str: Teks yang sudah dibersihkan
    """
    if not isinstance(text, str):
        return ''
    
    # Ubah ke lowercase
    text = text.lower()
    
    # Hapus karakter khusus dan angka
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Hapus whitespace berlebih
    text = ' '.join(text.split())
    
    return text

def get_stopwords():
    """
    Mendapatkan daftar stopwords dalam Bahasa Indonesia
    
    Returns:
        set: Kumpulan stopwords
    """
    try:
        # Stopwords Bahasa Indonesia
        indonesian_stopwords = set(stopwords.words('indonesian'))
    except:
        # Stopwords manual jika download gagal
        indonesian_stopwords = {
            'yang', 'di', 'ke', 'dari', 'pada', 'dalam', 'untuk', 
            'tentang', 'dengan', 'dan', 'atau', 'ini', 'itu', 
            'bagi', 'saat', 'sudah', 'akan', 'telah', 'oleh', 
            'setelah', 'karena', 'serta', 'dapat', 'bisa', 
            'masih', 'juga', 'ada', 'adalah', 'tersebut'
        }
    
    # Tambahan stopwords spesifik
    additional_stopwords = {
        'nya', 'para', 'demi', 'antar', 'jakarta', 'indonesia'
    }
    
    return indonesian_stopwords.union(additional_stopwords)
```
