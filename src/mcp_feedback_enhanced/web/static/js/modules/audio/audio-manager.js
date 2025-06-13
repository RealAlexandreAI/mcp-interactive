/**
 * MCP Feedback Enhanced - 音效管理模組
 * ===================================
 * 
 * 處理音效通知的播放、管理和設定功能
 * 使用 HTML5 Audio API 進行音效播放
 * 支援自訂音效上傳和 base64 儲存
 */

(function() {
    'use strict';

    // 確保命名空間存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * 音效管理器建構函數
     */
    function AudioManager(options) {
        options = options || {};
        
        // 設定管理器引用
        this.settingsManager = options.settingsManager || null;
        
        // 當前音效設定
        this.currentAudioSettings = {
            enabled: false,
            volume: 50,
            selectedAudioId: 'default-beep',
            customAudios: []
        };
        
        // 預設音效（base64 編碼的簡單提示音）
        this.defaultAudios = {
            'default-beep': {
                id: 'default-beep',
                name: '經典提示音',
                data: this.generateBeepSound(),
                mimeType: 'audio/wav',
                isDefault: true
            },
            'notification-ding': {
                id: 'notification-ding',
                name: '通知鈴聲',
                data: this.generateDingSound(),
                mimeType: 'audio/wav',
                isDefault: true
            },
            'soft-chime': {
                id: 'soft-chime',
                name: '輕柔鐘聲',
                data: this.generateChimeSound(),
                mimeType: 'audio/wav',
                isDefault: true
            }
        };
        
        // 當前播放的 Audio 物件
        this.currentAudio = null;
        
        // 回調函數
        this.onSettingsChange = options.onSettingsChange || null;
        
        console.log('🔊 AudioManager 初始化完成');
    }

    /**
     * 初始化音效管理器
     */
    AudioManager.prototype.initialize = function() {
        this.loadAudioSettings();
        console.log('✅ AudioManager 初始化完成');
    };

    /**
     * 載入音效設定
     */
    AudioManager.prototype.loadAudioSettings = function() {
        if (!this.settingsManager) {
            console.warn('⚠️ SettingsManager 未設定，使用預設音效設定');
            return;
        }

        try {
            // 從設定管理器載入音效相關設定
            this.currentAudioSettings.enabled = this.settingsManager.get('audioNotificationEnabled', false);
            this.currentAudioSettings.volume = this.settingsManager.get('audioNotificationVolume', 50);
            this.currentAudioSettings.selectedAudioId = this.settingsManager.get('selectedAudioId', 'default-beep');
            this.currentAudioSettings.customAudios = this.settingsManager.get('customAudios', []);
            
            console.log('📥 音效設定已載入:', this.currentAudioSettings);
        } catch (error) {
            console.error('❌ 載入音效設定失敗:', error);
        }
    };

    /**
     * 儲存音效設定
     */
    AudioManager.prototype.saveAudioSettings = function() {
        if (!this.settingsManager) {
            console.warn('⚠️ SettingsManager 未設定，無法儲存音效設定');
            return;
        }

        try {
            this.settingsManager.set('audioNotificationEnabled', this.currentAudioSettings.enabled);
            this.settingsManager.set('audioNotificationVolume', this.currentAudioSettings.volume);
            this.settingsManager.set('selectedAudioId', this.currentAudioSettings.selectedAudioId);
            this.settingsManager.set('customAudios', this.currentAudioSettings.customAudios);
            
            console.log('💾 音效設定已儲存');
            
            // 觸發回調
            if (this.onSettingsChange) {
                this.onSettingsChange(this.currentAudioSettings);
            }
        } catch (error) {
            console.error('❌ 儲存音效設定失敗:', error);
        }
    };

    /**
     * 播放通知音效
     */
    AudioManager.prototype.playNotification = function() {
        if (!this.currentAudioSettings.enabled) {
            console.log('🔇 音效通知已停用');
            return;
        }

        try {
            const audioData = this.getAudioById(this.currentAudioSettings.selectedAudioId);
            if (!audioData) {
                console.warn('⚠️ 找不到指定的音效，使用預設音效');
                this.playAudio(this.defaultAudios['default-beep']);
                return;
            }

            this.playAudio(audioData);
        } catch (error) {
            console.error('❌ 播放通知音效失敗:', error);
        }
    };

    /**
     * 播放指定的音效
     */
    AudioManager.prototype.playAudio = function(audioData) {
        try {
            // 停止當前播放的音效
            if (this.currentAudio) {
                this.currentAudio.pause();
                this.currentAudio = null;
            }

            // 建立新的 Audio 物件
            this.currentAudio = new Audio();
            this.currentAudio.src = 'data:' + audioData.mimeType + ';base64,' + audioData.data;
            this.currentAudio.volume = this.currentAudioSettings.volume / 100;

            // 播放音效
            const playPromise = this.currentAudio.play();
            
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        console.log('🔊 音效播放成功:', audioData.name);
                    })
                    .catch(error => {
                        console.error('❌ 音效播放失敗:', error);
                        // 可能是瀏覽器的自動播放政策限制
                        if (error.name === 'NotAllowedError') {
                            console.warn('⚠️ 瀏覽器阻止自動播放，需要用戶互動');
                        }
                    });
            }
        } catch (error) {
            console.error('❌ 播放音效時發生錯誤:', error);
        }
    };

    /**
     * 根據 ID 獲取音效資料
     */
    AudioManager.prototype.getAudioById = function(audioId) {
        // 先檢查預設音效
        if (this.defaultAudios[audioId]) {
            return this.defaultAudios[audioId];
        }

        // 再檢查自訂音效
        return this.currentAudioSettings.customAudios.find(audio => audio.id === audioId) || null;
    };

    /**
     * 獲取所有可用的音效
     */
    AudioManager.prototype.getAllAudios = function() {
        const allAudios = [];
        
        // 新增預設音效
        Object.values(this.defaultAudios).forEach(audio => {
            allAudios.push(audio);
        });
        
        // 新增自訂音效
        this.currentAudioSettings.customAudios.forEach(audio => {
            allAudios.push(audio);
        });
        
        return allAudios;
    };

    /**
     * 新增自訂音效
     */
    AudioManager.prototype.addCustomAudio = function(name, file) {
        return new Promise((resolve, reject) => {
            if (!name || !file) {
                reject(new Error('音效名稱和檔案不能為空'));
                return;
            }

            // 檢查檔案類型
            if (!this.isValidAudioFile(file)) {
                reject(new Error('不支援的音效檔案格式'));
                return;
            }

            // 檢查名稱是否重複
            if (this.isAudioNameExists(name)) {
                reject(new Error('音效名稱已存在'));
                return;
            }

            // 轉換為 base64
            this.fileToBase64(file)
                .then(base64Data => {
                    const audioData = {
                        id: this.generateAudioId(),
                        name: name.trim(),
                        data: base64Data,
                        mimeType: file.type,
                        createdAt: new Date().toISOString(),
                        isDefault: false
                    };

                    this.currentAudioSettings.customAudios.push(audioData);
                    this.saveAudioSettings();

                    console.log('➕ 新增自訂音效:', audioData.name);
                    resolve(audioData);
                })
                .catch(error => {
                    reject(error);
                });
        });
    };

    /**
     * 刪除自訂音效
     */
    AudioManager.prototype.removeCustomAudio = function(audioId) {
        const index = this.currentAudioSettings.customAudios.findIndex(audio => audio.id === audioId);
        if (index === -1) {
            throw new Error('找不到指定的音效');
        }

        const removedAudio = this.currentAudioSettings.customAudios.splice(index, 1)[0];
        
        // 如果刪除的是當前選中的音效，切換到預設音效
        if (this.currentAudioSettings.selectedAudioId === audioId) {
            this.currentAudioSettings.selectedAudioId = 'default-beep';
        }

        this.saveAudioSettings();
        console.log('🗑️ 刪除自訂音效:', removedAudio.name);
        
        return removedAudio;
    };

    /**
     * 設定音量
     */
    AudioManager.prototype.setVolume = function(volume) {
        if (volume < 0 || volume > 100) {
            throw new Error('音量必須在 0-100 之間');
        }

        this.currentAudioSettings.volume = volume;
        this.saveAudioSettings();
        console.log('🔊 音量已設定為:', volume);
    };

    /**
     * 設定是否啟用音效通知
     */
    AudioManager.prototype.setEnabled = function(enabled) {
        this.currentAudioSettings.enabled = !!enabled;
        this.saveAudioSettings();
        console.log('🔊 音效通知已', enabled ? '啟用' : '停用');
    };

    /**
     * 設定選中的音效
     */
    AudioManager.prototype.setSelectedAudio = function(audioId) {
        if (!this.getAudioById(audioId)) {
            throw new Error('找不到指定的音效');
        }

        this.currentAudioSettings.selectedAudioId = audioId;
        this.saveAudioSettings();
        console.log('🎵 已選擇音效:', audioId);
    };

    /**
     * 檢查是否為有效的音效檔案
     */
    AudioManager.prototype.isValidAudioFile = function(file) {
        const validTypes = ['audio/mp3', 'audio/wav', 'audio/ogg', 'audio/mpeg'];
        return validTypes.includes(file.type);
    };

    /**
     * 檢查音效名稱是否已存在
     */
    AudioManager.prototype.isAudioNameExists = function(name) {
        // 檢查預設音效
        const defaultExists = Object.values(this.defaultAudios).some(audio => audio.name === name);
        if (defaultExists) return true;

        // 檢查自訂音效
        return this.currentAudioSettings.customAudios.some(audio => audio.name === name);
    };

    /**
     * 檔案轉 base64
     */
    AudioManager.prototype.fileToBase64 = function(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function() {
                // 移除 data URL 前綴，只保留 base64 資料
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = function() {
                reject(new Error('檔案讀取失敗'));
            };
            reader.readAsDataURL(file);
        });
    };

    /**
     * 生成音效 ID
     */
    AudioManager.prototype.generateAudioId = function() {
        return 'audio_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    };

    /**
     * 生成經典提示音（440Hz，0.3秒）
     */
    AudioManager.prototype.generateBeepSound = function() {
        return this.generateToneWAV(440, 0.3, 0.5);
    };

    /**
     * 生成通知鈴聲（800Hz + 600Hz 和弦，0.4秒）
     */
    AudioManager.prototype.generateDingSound = function() {
        return this.generateToneWAV(800, 0.4, 0.4);
    };

    /**
     * 生成輕柔鐘聲（523Hz，0.5秒，漸弱）
     */
    AudioManager.prototype.generateChimeSound = function() {
        return this.generateToneWAV(523, 0.5, 0.3);
    };

    /**
     * 生成指定頻率和時長的 WAV 音效
     * @param {number} frequency - 頻率（Hz）
     * @param {number} duration - 持續時間（秒）
     * @param {number} volume - 音量（0-1）
     */
    AudioManager.prototype.generateToneWAV = function(frequency, duration, volume) {
        const sampleRate = 44100;
        const numSamples = Math.floor(sampleRate * duration);
        const buffer = new ArrayBuffer(44 + numSamples * 2);
        const view = new DataView(buffer);

        // WAV 檔案標頭
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, 36 + numSamples * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, 1, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * 2, true);
        view.setUint16(32, 2, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, numSamples * 2, true);

        // 生成音效資料
        for (let i = 0; i < numSamples; i++) {
            const t = i / sampleRate;
            const fadeOut = Math.max(0, 1 - (t / duration) * 0.5); // 漸弱效果
            const sample = Math.sin(2 * Math.PI * frequency * t) * volume * fadeOut;
            const intSample = Math.max(-32768, Math.min(32767, Math.floor(sample * 32767)));
            view.setInt16(44 + i * 2, intSample, true);
        }

        // 轉換為 base64
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.length; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    };

    /**
     * 獲取當前設定
     */
    AudioManager.prototype.getSettings = function() {
        return Utils.deepClone(this.currentAudioSettings);
    };

    // 匯出到全域命名空間
    window.MCPFeedback.AudioManager = AudioManager;

})();
