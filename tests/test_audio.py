import os
import pytest
from Audio_processor_Rassylshikov import AudioProcessor

TEST_DIR = os.path.dirname(__file__)
SAMPLE_WAV = os.path.join(TEST_DIR, "../test_files/sample.wav")
OUTPUT_WAV = os.path.join(TEST_DIR, "../test_files/output.wav")


# 1. Тест загрузки WAV и получения метаданных
def test_load_wav_and_get_info():
    processor = AudioProcessor(SAMPLE_WAV)
    info = processor.get_audio_info()

    assert info['duration'] > 0
    assert info['channels'] in [1, 2]
    assert info['sample_rate'] in [8000, 16000, 22050, 44100, 48000]
    assert info['bit_depth'] in [8, 16, 24, 32]


# 2. Тест обрезки аудио
def test_trim_audio():
    processor = AudioProcessor(SAMPLE_WAV)
    original_duration = processor.get_duration()

    start = 0.5
    end = original_duration - 0.5
    processor.trim(start, end)

    new_duration = processor.get_duration()
    expected_duration = end - start

    assert abs(new_duration - expected_duration) < 0.01


# 3. Тест изменения громкости и сохранения
def test_change_volume_and_save():
    processor = AudioProcessor(SAMPLE_WAV)
    processor.change_volume(-10)  # Уменьшаем громкость на 10 dB

    processor.save(OUTPUT_WAV)
    assert os.path.exists(OUTPUT_WAV)

    # Проверяем, что файл сохранён и загружается
    new_processor = AudioProcessor(OUTPUT_WAV)
    assert new_processor.get_duration() == processor.get_duration()

    # Удаляем временный файл
    os.remove(OUTPUT_WAV)