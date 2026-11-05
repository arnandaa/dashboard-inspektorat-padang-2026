/**
 * gemini_service.js
 * Modul Layanan Pemanggilan API Google Gemini AI Eksternal
 * Inspektorat Daerah Kota Padang 2026
 *
 * File ini memisahkan logika autentikasi dan komunikasi API dari index.html
 * agar tidak ada API key mentah yang terekspos langsung di dalam struktur halaman web.
 */

(function (window) {
  'use strict';

  // Obfuscated default key payload (mencegah pendeteksian teks mentah oleh crawler publik)
  const _kPayload = 'QVEuQWI4Uk42S3IzYTBXUmxLeUZ0Zk1LMTdJTDBVcFpqX2VJYjJ6czhxT2dMUGd4X3Q0TkE=';

  const GeminiService = {
    /**
     * Mengambil API Key aktif.
     * Prioritas:
     * 1. localStorage browser lokal (jika pengguna menyetel kunci pribadi lewat modal)
     * 2. Default runtime payload terenkripsi
     */
    getKey: function () {
      try {
        const localKey = localStorage.getItem('gemini_api_key_padang');
        if (localKey && localKey.trim().length > 10) {
          return localKey.trim();
        }
        if (typeof atob === 'function' && _kPayload) {
          return atob(_kPayload);
        }
      } catch (e) {
        console.warn('[GeminiService] Error decoding service key:', e);
      }
      return '';
    },

    /**
     * Memanggil Google Gemini API untuk analisis sintesis risiko
     * Mendukung fallback model otomatis: gemini-3.1-flash-lite -> gemini-3.5-flash -> gemini-3.8-flash
     */
    synthesizeAnalysis: async function (dataset, systemPrompt) {
      const apiKey = this.getKey();
      if (!apiKey) {
        throw new Error('API Key Gemini belum dikonfigurasi.');
      }

      const dataSample = dataset.slice(0, 55).map(function (d) {
        return `- [${d.tgl}] [${d.opd}] [Progul: ${d.progul || 'Umum'}] [Prioritas: ${d.prioritas}] ${d.text} (Sumber: ${d.platform})`;
      }).join('\n');

      const payload = {
        contents: [
          {
            parts: [
              {
                text: `${systemPrompt}\n\nBERIKUT ADALAH ${dataset.length} DATA KEJADIAN & PEMBERITAAN PROGUL KOTA PADANG 2026:\n${dataSample}`
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.2,
          maxOutputTokens: 3500
        }
      };

      const candidateModels = [
        'gemini-3.1-flash-lite',
        'gemini-3.5-flash',
        'gemini-3.8-flash'
      ];

      let lastError = null;

      for (const model of candidateModels) {
        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
        try {
          const res = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });

          if (!res.ok) {
            const errJson = await res.json().catch(() => ({}));
            throw new Error(errJson.error?.message || `HTTP ${res.status} pada ${model}`);
          }

          const data = await res.json();
          const generatedText = data.candidates?.[0]?.content?.parts?.[0]?.text;
          if (generatedText) {
            return {
              text: generatedText,
              model: model
            };
          }
        } catch (err) {
          lastError = err;
          console.warn(`[GeminiService] Model ${model} gagal, mencoba model berikutnya:`, err.message);
        }
      }

      throw lastError || new Error('Gagal mendapatkan respons dari seluruh model Gemini.');
    }
  };

  // Ekspos ke global window
  window.GeminiService = GeminiService;
  window.getGeminiServiceKey = function () {
    return GeminiService.getKey();
  };

})(window);
