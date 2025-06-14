#!/usr/bin/env python3
"""
English to Hindi Text Transformer
Performs three types of transformations:
1. English in Devanagari script (transliteration)
2. Hindi in Devanagari script (translation)
3. Hindi in Roman script (romanization)
"""

import re
import os
from dotenv import load_dotenv
import streamlit as st
from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import google.generativeai as genai

# Load environment variables
load_dotenv()

class TextTransformer:
    def __init__(self):
        self.translator = Translator()
        
        # Initialize Google AI API
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key and api_key.strip() and not api_key.startswith('your_'):
            try:
                genai.configure(api_key=api_key)
                # Try multiple model names to find the working one
                model_names = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
                
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Try a simple test to validate the key and model
                        test_response = self.model.generate_content("Test")
                        self.use_gemini = True
                        st.success(f"✅ Google Gemini API connected successfully with model: {model_name}")
                        break
                    except Exception as model_error:
                        continue
                
                if not hasattr(self, 'use_gemini') or not self.use_gemini:
                    raise Exception("No working Gemini model found")
                    
            except Exception as e:
                self.use_gemini = False
                st.warning(f"⚠️ Google API key issue: {str(e)}. Using Google Translate as fallback.")
        else:
            self.use_gemini = False
            if not api_key:
                st.info("ℹ️ No Google API key found in .env file. Using Google Translate.")
            else:
                st.warning("⚠️ Invalid Google API key format. Using Google Translate as fallback.")
        
        # Comprehensive English to Devanagari phonetic mapping
        self.eng_to_dev_map = {
            # Single letters - improved phonetic mapping
            'a': 'अ', 'b': 'ब', 'c': 'क', 'd': 'द', 'e': 'ई', 'f': 'फ',
            'g': 'ग', 'h': 'ह', 'i': 'आई', 'j': 'ज', 'k': 'क', 'l': 'ल',
            'm': 'म', 'n': 'न', 'o': 'ओ', 'p': 'प', 'q': 'क्यू', 'r': 'आर', 
            's': 'एस', 't': 'ट', 'u': 'यू', 'v': 'वी', 'w': 'डब्ल्यू', 
            'x': 'एक्स', 'y': 'वाई', 'z': 'जेड',
            
            # Common consonant combinations
            'th': 'थ', 'sh': 'श', 'ch': 'च', 'ph': 'फ', 'gh': 'घ',
            'kh': 'ख', 'dh': 'ध', 'bh': 'भ', 'jh': 'झ', 'ng': 'ंग',
            'ck': 'क', 'st': 'स्ट', 'sp': 'स्प', 'sc': 'स्क', 'sk': 'स्क',
            
            # Vowel combinations and sounds
            'aa': 'आ', 'ee': 'ई', 'ii': 'ई', 'oo': 'ऊ', 'uu': 'ऊ',
            'ai': 'ऐ', 'ay': 'ए', 'au': 'औ', 'aw': 'ऑ', 'ey': 'ए',
            'ou': 'ओ', 'ow': 'आउ', 'oy': 'ऑय', 'ea': 'ई', 'ie': 'आई',
            'oa': 'ओ', 'ue': 'यू', 'ui': 'यूआई', 'eu': 'यू',
            
            # Common words - high frequency
            'the': 'द', 'and': 'एंड', 'are': 'आर', 'you': 'यू', 'for': 'फॉर',
            'not': 'नॉट', 'but': 'बट', 'can': 'कैन', 'all': 'ऑल', 'any': 'एनी',
            'had': 'हैड', 'her': 'हर', 'was': 'वॉज़', 'one': 'वन', 'our': 'आवर',
            'out': 'आउट', 'day': 'डे', 'get': 'गेट', 'has': 'हैज़', 'him': 'हिम',
            'his': 'हिज़', 'how': 'हाउ', 'man': 'मैन', 'new': 'न्यू', 'now': 'नाउ',
            'old': 'ओल्ड', 'see': 'सी', 'two': 'टू', 'way': 'वे', 'who': 'हू',
            'boy': 'बॉय', 'did': 'डिड', 'its': 'इट्स', 'let': 'लेट', 'put': 'पुट',
            'say': 'से', 'she': 'शी', 'too': 'टू', 'use': 'यूज़', 'what': 'व्हाट',
            'when': 'व्हेन', 'where': 'व्हेयर', 'why': 'व्हाई', 'with': 'विथ',
            'will': 'विल', 'were': 'वर', 'been': 'बीन', 'have': 'हैव',
            'this': 'दिस', 'that': 'दैट', 'they': 'दे', 'them': 'देम',
            'there': 'देयर', 'then': 'देन', 'than': 'दैन', 'these': 'दीज़',
            'those': 'दोज़', 'think': 'थिंक', 'through': 'थ्रू', 'time': 'टाइम',
            'take': 'टेक', 'tell': 'टेल', 'turn': 'टर्न', 'try': 'ट्राई',
            
            # Story-specific words
            'first': 'फर्स्ट', 'wife': 'वाइफ', 'wedding': 'वेडिंग', 'night': 'नाइट',
            'lying': 'लाइंग', 'bed': 'बेड', 'quietly': 'क्वाइटली', 'said': 'सेड',
            'die': 'डाई', 'died': 'डाइड', 'life': 'लाइफ', 'born': 'बॉर्न',
            'married': 'मैरिड', 'marry': 'मैरी', 'guess': 'गेस', 'forgot': 'फॉरगॉट',
            'about': 'अबाउट', 'need': 'नीड', 'needing': 'नीडिंग', 'kid': 'किड',
            'child': 'चाइल्ड', 'suppose': 'सपोज़', 'might': 'माइट', 'led': 'लेड',
            'live': 'लिव', 'lived': 'लिव्ड', 'long': 'लॉन्ग', 'care': 'केयर',
            'take': 'टेक', 'daughter': 'डॉटर', 'remember': 'रिमेम्बर', 'mother': 'मदर',
            'even': 'ईवन', 'well': 'वेल', 'too': 'टू', 'doesnt': 'डज़न्ट',
            
            # Contractions and common patterns
            "don't": 'डोन्ट', "doesn't": 'डज़न्ट', "didn't": 'डिडन्ट', 
            "won't": 'वोन्ट', "can't": 'कान्ट', "isn't": 'इज़न्ट',
            "aren't": 'आरन्ट', "wasn't": 'वॉज़न्ट', "weren't": 'वरन्ट',
            "i'm": 'आइम', "you're": 'यूआर', "we're": 'वीआर', 
            "they're": 'देयर', "it's": 'इट्स', "that's": 'दैट्स',
            "what's": 'व्हाट्स', "where's": 'व्हेयर्स', "who's": 'हूज़',
            
            # Common endings
            'ing': 'इंग', 'tion': 'शन', 'sion': 'शन', 'er': 'र', 'ed': 'ड',
            'ly': 'ली', 'ty': 'टी', 'ry': 'री', 'al': 'ल', 'le': 'ल',
            'ment': 'मेंट', 'ness': 'नेस', 'able': 'एबल', 'ible': 'इबल'
        }
        
        # Hindi to Roman mapping for romanization
        self.hindi_to_roman_map = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
            'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
            'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
            'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
            'ष': 'sh', 'स': 's', 'ह': 'h', 'क्ष': 'ksh', 'त्र': 'tr',
            'ज्ञ': 'gya', 'ऋ': 'ri', 'ॐ': 'om'
        }

    def english_to_devanagari_transliteration(self, text):
        """
        Advanced transliteration of English text to Devanagari script
        """
        # Preserve original text structure
        lines = text.split('\n')
        result_lines = []
        
        for line in lines:
            if not line.strip():
                result_lines.append('')
                continue
                
            # Convert to lowercase for processing but preserve punctuation
            words = line.split()
            result_words = []
            
            for word in words:
                # Handle punctuation and quotes
                prefix = ''
                suffix = ''
                clean_word = word.lower()
                
                # Extract leading punctuation/quotes
                while clean_word and clean_word[0] in '"\'(':
                    prefix += clean_word[0]
                    clean_word = clean_word[1:]
                
                # Extract trailing punctuation/quotes
                while clean_word and clean_word[-1] in '.,!?;:)\'"…':
                    suffix = clean_word[-1] + suffix
                    clean_word = clean_word[:-1]
                
                if not clean_word:
                    result_words.append(word)
                    continue
                
                # Check if entire word is in mapping (most efficient)
                if clean_word in self.eng_to_dev_map:
                    result_words.append(prefix + self.eng_to_dev_map[clean_word] + suffix)
                    continue
                
                # Advanced word processing with syllable awareness
                word_result = self._transliterate_word_advanced(clean_word)
                result_words.append(prefix + word_result + suffix)
            
            result_lines.append(' '.join(result_words))
        
        return '\n'.join(result_lines)
    
    def _transliterate_word_advanced(self, word):
        """
        Advanced word-level transliteration with better phonetic rules
        """
        result = ""
        i = 0
        
        while i < len(word):
            matched = False
            
            # Try to match progressively shorter substrings
            for length in range(min(8, len(word) - i), 0, -1):
                if i + length <= len(word):
                    substring = word[i:i+length]
                    if substring in self.eng_to_dev_map:
                        result += self.eng_to_dev_map[substring]
                        i += length
                        matched = True
                        break
            
            if not matched:
                # Apply phonetic rules for unmapped characters
                char = word[i]
                if char.isalpha():
                    # Special case handling
                    if char == 'y' and i > 0:  # 'y' in middle/end often sounds like 'ी'
                        result += 'ी'
                    elif char == 'w' and i < len(word) - 1 and word[i+1] in 'aeiou':
                        result += 'व'  # 'w' before vowels
                    elif char in self.eng_to_dev_map:
                        result += self.eng_to_dev_map[char]
                    else:
                        result += char
                else:
                    result += char
                i += 1
        
        return result

    def english_to_hindi_translation(self, text):
        """
        Translate English text to Hindi using Google Gemini API or Google Translate
        """
        if self.use_gemini:
            try:
                input_prompt = f"""
You are an expert English to Hindi translator with deep knowledge of both languages.
Your task is to translate the given English text to natural, fluent Hindi.

Guidelines:
- Provide accurate and contextually appropriate Hindi translation
- Maintain the original meaning and tone
- Use proper Hindi grammar and sentence structure
- Keep the same paragraph structure and line breaks as the original
- Return only the Hindi translation without any explanations

English Text to Translate:
{text}

Hindi Translation:
"""
                response = self.model.generate_content(input_prompt)
                return response.text.strip()
            except Exception as e:
                st.error(f"Gemini API error: {e}")
                # Fallback to Google Translate
                return self._translate_with_googletrans(text)
        else:
            return self._translate_with_googletrans(text)
    
    def get_gemini_response(self, input_prompt):
        """
        Get response from Gemini API with error handling
        """
        try:
            response = self.model.generate_content(input_prompt)
            return response.text
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            return "Error getting response from Gemini API"
    
    def _translate_with_googletrans(self, text):
        """
        Fallback translation using Google Translate
        """
        try:
            translation = self.translator.translate(text, src='en', dest='hi')
            return translation.text
        except Exception as e:
            st.error(f"Translation error: {e}")
            return "Translation failed"

    def hindi_to_roman_transliteration(self, hindi_text):
        """
        Enhanced Hindi to Roman transliteration with better readability
        """
        try:
            # Using indic-transliteration library for base conversion
            roman_text = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS)
            
            # Enhanced post-processing for better readability
            roman_text = self._clean_romanization(roman_text)
            
            return roman_text
            
        except Exception as e:
            st.error(f"Romanization error: {e}")
            # Enhanced fallback to manual mapping
            return self._enhanced_manual_hindi_to_roman(hindi_text)
    
    def _clean_romanization(self, text):
        """
        Clean and improve the romanized text for better readability
        """
        # Remove unwanted symbols
        text = text.replace('~', '').replace('|', '').replace('^', '')
        
        # Improve common patterns
        replacements = {
            # Better vowel representations
            'aa': 'aa', 'ii': 'ee', 'uu': 'oo', 'R^i': 'ri', 'RRi': 'ri',
            
            # Better consonant combinations
            'kh': 'kh', 'gh': 'gh', 'ch': 'ch', 'jh': 'jh', 'ñ': 'ny',
            'th': 'th', 'dh': 'dh', 'ph': 'ph', 'bh': 'bh', 'sh': 'sh',
            
            # Fix common transliteration issues
            'M': 'm', 'H': 'h', '.n': 'n', '.m': 'm', '.h': 'h',
            '.t': 't', '.d': 'd', '.s': 's', '.r': 'r', '.l': 'l',
            
            # Better word endings
            'ti': 'ti', 'te': 'te', 'ta': 'ta', 'tu': 'tu',
            'ni': 'ni', 'ne': 'ne', 'na': 'na', 'nu': 'nu',
            
            # Fix spacing issues
            ' .': '.', ' ,': ',', ' !': '!', ' ?': '?',
            ' ;': ';', ' :': ':', "' ": "'", ' "': '"'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Capitalize first letter of sentences
        sentences = text.split('. ')
        capitalized = []
        for sentence in sentences:
            if sentence:
                sentence = sentence.strip()
                if sentence:
                    sentence = sentence[0].upper() + sentence[1:] if len(sentence) > 1 else sentence.upper()
            capitalized.append(sentence)
        
        result = '. '.join(capitalized)
        
        # Ensure first character is uppercase
        if result and result[0].islower():
            result = result[0].upper() + result[1:]
        
        return result
    
    def _enhanced_manual_hindi_to_roman(self, hindi_text):
        """
        Enhanced fallback manual Hindi to Roman conversion
        """
        # Extended mapping for better results
        enhanced_map = {
            # Vowels
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'अं': 'an', 'अः': 'ah',
            
            # Consonants with better mapping
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
            'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
            'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
            'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
            'ष': 'sh', 'स': 's', 'ह': 'h', 'क्ष': 'ksh', 'त्र': 'tr',
            'ज्ञ': 'gya', 'ऋ': 'ri', 'ॐ': 'om',
            
            # Matras (vowel signs)
            'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
            'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', 'ः': 'h',
            '्': '', 'ँ': 'n'
        }
        
        result = ""
        for char in hindi_text:
            if char in enhanced_map:
                result += enhanced_map[char]
            elif char.isspace() or not char.isalpha():
                result += char
            else:
                result += char
        
        # Clean up and capitalize properly
        result = self._clean_romanization(result)
        return result

    def _manual_hindi_to_roman(self, hindi_text):
        """
        Fallback manual Hindi to Roman conversion
        """
        result = ""
        for char in hindi_text:
            if char in self.hindi_to_roman_map:
                result += self.hindi_to_roman_map[char]
            elif char.isspace() or not char.isalpha():
                result += char
            else:
                result += char  # Keep unmapped characters
        return result.title()

    def transform_text(self, input_text):
        """
        Perform all three transformations on the input text
        """
        results = {}
        
        with st.spinner('Performing transformations...'):
            # 1. English in Devanagari script (transliteration)
            eng_devanagari = self.english_to_devanagari_transliteration(input_text)
            results['english_devanagari'] = eng_devanagari
            
            # 2. Hindi in Devanagari script (translation)
            hindi_devanagari = self.english_to_hindi_translation(input_text)
            results['hindi_devanagari'] = hindi_devanagari
            
            # 3. Hindi in Roman script (romanization)
            hindi_roman = self.hindi_to_roman_transliteration(hindi_devanagari)
            results['hindi_roman'] = hindi_roman
        
        return results

def streamlit_app():
    st.set_page_config(
        page_title="English to Hindi Text Transformer",
        page_icon="🔤",
        layout="wide"
    )
    
    st.title("🔤 English to Hindi Text Transformer")
    st.markdown("Transform English text into three different formats:")
    st.markdown("1. **English in Devanagari script** (phonetic transliteration)")
    st.markdown("2. **Hindi in Devanagari script** (meaning translation)")
    st.markdown("3. **Hindi in Roman script** (romanized Hindi)")
    
    # Add API status info
    if 'transformer' not in st.session_state:
        st.session_state.transformer = TextTransformer()
    
    # Show API status
    if st.session_state.transformer.use_gemini:
        st.info("🚀 Using Google Gemini API for high-quality translation")
    else:
        st.info("🔄 Using Google Translate as translation service")
    
    st.divider()
    
    # Initialize transformer
    # (transformer already initialized above for API status check)
    
    # Input section
    st.subheader("📝 Input Text")
    input_text = st.text_area(
        "Enter English text:",
        height=150,
        placeholder="Type your English text here...\nYou can enter as many lines as you want."
    )
    
    if st.button("🔄 Transform Text", type="primary"):
        if not input_text.strip():
            st.error("Please enter some text.")
        else:
            # Process the text - no line limit restrictions
            results = st.session_state.transformer.transform_text(input_text)
            
            # Display results
            st.divider()
            st.subheader("📋 Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 🔤 English in Devanagari")
                st.markdown(f"**{results['english_devanagari']}**")
                
            with col2:
                st.markdown("### Hindi in Devanagari")
                st.markdown(f"**{results['hindi_devanagari']}**")
                
            with col3:
                st.markdown("### 🔡 Hindi in Roman Script")
                st.markdown(f"**{results['hindi_roman']}**")
            
            # Copy buttons
            st.divider()
            st.subheader("📋 Copy Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.code(results['english_devanagari'], language=None)
            with col2:
                st.code(results['hindi_devanagari'], language=None)
            with col3:
                st.code(results['hindi_roman'], language=None)

def main():
    # Check if running in Streamlit
    try:
        streamlit_app()
    except:
        # Fallback to command line interface
        transformer = TextTransformer()
        
        print("English to Hindi Text Transformer")
        print("=" * 40)
        
        while True:
            try:
                user_input = input("\nEnter English text or 'quit' to exit:\n")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input.strip():
                    print("Please enter some text.")
                    continue
                
                # Process the text - no line limit restrictions
                results = transformer.transform_text(user_input)
                
                print(f"Input: {user_input}")
                print("-" * 50)
                print(f"English in Devanagari: **{results['english_devanagari']}**")
                print(f"Hindi in Devanagari: **{results['hindi_devanagari']}**")
                print(f"Hindi in Roman: **{results['hindi_roman']}**")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()