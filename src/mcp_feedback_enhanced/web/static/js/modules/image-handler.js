/**
 * MCP Feedback Enhanced - 圖片處理模組
 * ==================================
 * 
 * 處理圖片上傳、預覽、壓縮和管理功能
 */

(function() {
    'use strict';

    // 確保命名空間和依賴存在
    window.MCPFeedback = window.MCPFeedback || {};
    const Utils = window.MCPFeedback.Utils;

    /**
     * 圖片處理器建構函數
     */
    function ImageHandler(options) {
        options = options || {};
        
        this.images = [];
        this.imageSizeLimit = options.imageSizeLimit || 0;
        this.enableBase64Detail = options.enableBase64Detail || false;
        this.layoutMode = options.layoutMode || 'combined-vertical';
        this.currentImagePrefix = '';
        
        // UI 元素
        this.imageInput = null;
        this.imageUploadArea = null;
        this.imagePreviewContainer = null;
        this.imageSizeLimitSelect = null;
        this.enableBase64DetailCheckbox = null;
        
        // 事件處理器
        this.imageChangeHandler = null;
        this.imageClickHandler = null;
        this.imageDragOverHandler = null;
        this.imageDragLeaveHandler = null;
        this.imageDropHandler = null;
        this.pasteHandler = null;
        
        // 回調函數
        this.onSettingsChange = options.onSettingsChange || null;
    }

    /**
     * 初始化圖片處理器
     */
    ImageHandler.prototype.init = function() {
        console.log('🖼️ 開始初始化圖片處理功能...');
        
        this.initImageElements();
        this.setupImageEventListeners();
        this.setupGlobalPasteHandler();
        
        console.log('✅ 圖片處理功能初始化完成');
    };

    /**
     * 動態初始化圖片相關元素
     */
    ImageHandler.prototype.initImageElements = function() {
        const prefix = this.layoutMode && this.layoutMode.startsWith('combined') ? 'combined' : 'feedback';
        
        console.log('🖼️ 初始化圖片元素，使用前綴: ' + prefix);
        
        this.imageInput = Utils.safeQuerySelector('#' + prefix + 'ImageInput') || 
                         Utils.safeQuerySelector('#imageInput');
        this.imageUploadArea = Utils.safeQuerySelector('#' + prefix + 'ImageUploadArea') || 
                              Utils.safeQuerySelector('#imageUploadArea');
        this.imagePreviewContainer = Utils.safeQuerySelector('#' + prefix + 'ImagePreviewContainer') || 
                                    Utils.safeQuerySelector('#imagePreviewContainer');
        this.imageSizeLimitSelect = Utils.safeQuerySelector('#' + prefix + 'ImageSizeLimit') || 
                                   Utils.safeQuerySelector('#imageSizeLimit');
        this.enableBase64DetailCheckbox = Utils.safeQuerySelector('#' + prefix + 'EnableBase64Detail') || 
                                         Utils.safeQuerySelector('#enableBase64Detail');
        
        this.currentImagePrefix = prefix;
        
        if (!this.imageInput || !this.imageUploadArea) {
            console.warn('⚠️ 圖片元素初始化失敗 - imageInput: ' + !!this.imageInput + ', imageUploadArea: ' + !!this.imageUploadArea);
        } else {
            console.log('✅ 圖片元素初始化成功 - 前綴: ' + prefix);
        }
    };

    /**
     * 設置圖片事件監聽器
     */
    ImageHandler.prototype.setupImageEventListeners = function() {
        if (!this.imageInput || !this.imageUploadArea) {
            console.warn('⚠️ 缺少必要的圖片元素，跳過事件監聽器設置');
            return;
        }

        console.log('🖼️ 設置圖片事件監聽器 - imageInput: ' + this.imageInput.id + ', imageUploadArea: ' + this.imageUploadArea.id);

        // 移除舊的事件監聽器
        this.removeImageEventListeners();

        const self = this;

        // 文件選擇事件
        this.imageChangeHandler = function(e) {
            console.log('📁 文件選擇事件觸發 - input: ' + e.target.id + ', files: ' + e.target.files.length);
            self.handleFileSelect(e.target.files);
        };
        this.imageInput.addEventListener('change', this.imageChangeHandler);

        // 點擊上傳區域
        this.imageClickHandler = function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (self.imageInput) {
                console.log('🖱️ 點擊上傳區域 - 觸發 input: ' + self.imageInput.id);
                self.imageInput.click();
            }
        };
        this.imageUploadArea.addEventListener('click', this.imageClickHandler);

        // 拖放事件
        this.imageDragOverHandler = function(e) {
            e.preventDefault();
            self.imageUploadArea.classList.add('dragover');
        };
        this.imageUploadArea.addEventListener('dragover', this.imageDragOverHandler);

        this.imageDragLeaveHandler = function(e) {
            e.preventDefault();
            self.imageUploadArea.classList.remove('dragover');
        };
        this.imageUploadArea.addEventListener('dragleave', this.imageDragLeaveHandler);

        this.imageDropHandler = function(e) {
            e.preventDefault();
            self.imageUploadArea.classList.remove('dragover');
            self.handleFileSelect(e.dataTransfer.files);
        };
        this.imageUploadArea.addEventListener('drop', this.imageDropHandler);

        // 初始化圖片設定事件
        this.initImageSettings();
    };

    /**
     * 設置全域剪貼板貼上事件
     */
    ImageHandler.prototype.setupGlobalPasteHandler = function() {
        if (this.pasteHandler) {
            return; // 已經設置過了
        }

        const self = this;
        this.pasteHandler = function(e) {
            const items = e.clipboardData.items;
            for (let i = 0; i < items.length; i++) {
                const item = items[i];
                if (item.type.indexOf('image') !== -1) {
                    e.preventDefault();
                    const file = item.getAsFile();
                    self.handleFileSelect([file]);
                    break;
                }
            }
        };
        
        document.addEventListener('paste', this.pasteHandler);
        console.log('✅ 全域剪貼板貼上事件已設置');
    };

    /**
     * 移除圖片事件監聽器
     */
    ImageHandler.prototype.removeImageEventListeners = function() {
        if (this.imageInput && this.imageChangeHandler) {
            this.imageInput.removeEventListener('change', this.imageChangeHandler);
        }
        
        if (this.imageUploadArea) {
            if (this.imageClickHandler) {
                this.imageUploadArea.removeEventListener('click', this.imageClickHandler);
            }
            if (this.imageDragOverHandler) {
                this.imageUploadArea.removeEventListener('dragover', this.imageDragOverHandler);
            }
            if (this.imageDragLeaveHandler) {
                this.imageUploadArea.removeEventListener('dragleave', this.imageDragLeaveHandler);
            }
            if (this.imageDropHandler) {
                this.imageUploadArea.removeEventListener('drop', this.imageDropHandler);
            }
        }
    };

    /**
     * 初始化圖片設定事件
     */
    ImageHandler.prototype.initImageSettings = function() {
        const self = this;
        
        if (this.imageSizeLimitSelect) {
            this.imageSizeLimitSelect.addEventListener('change', function(e) {
                self.imageSizeLimit = parseInt(e.target.value);
                if (self.onSettingsChange) {
                    self.onSettingsChange();
                }
            });
        }

        if (this.enableBase64DetailCheckbox) {
            this.enableBase64DetailCheckbox.addEventListener('change', function(e) {
                self.enableBase64Detail = e.target.checked;
                if (self.onSettingsChange) {
                    self.onSettingsChange();
                }
            });
        }
    };

    /**
     * 處理文件選擇
     */
    ImageHandler.prototype.handleFileSelect = function(files) {
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.type.startsWith('image/')) {
                this.addImage(file);
            }
        }
    };

    /**
     * 添加圖片
     */
    ImageHandler.prototype.addImage = function(file) {
        // 檢查文件大小
        if (this.imageSizeLimit > 0 && file.size > this.imageSizeLimit) {
            Utils.showMessage('圖片大小超過限制 (' + Utils.formatFileSize(this.imageSizeLimit) + ')', Utils.CONSTANTS.MESSAGE_WARNING);
            return;
        }

        const self = this;
        this.fileToBase64(file)
            .then(function(base64) {
                const imageData = {
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    data: base64
                };

                self.images.push(imageData);
                self.updateImagePreview();
            })
            .catch(function(error) {
                console.error('圖片處理失敗:', error);
                Utils.showMessage('圖片處理失敗，請重試', Utils.CONSTANTS.MESSAGE_ERROR);
            });
    };

    /**
     * 將文件轉換為 Base64
     */
    ImageHandler.prototype.fileToBase64 = function(file) {
        return new Promise(function(resolve, reject) {
            const reader = new FileReader();
            reader.onload = function() {
                resolve(reader.result.split(',')[1]);
            };
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    };

    /**
     * 更新圖片預覽
     */
    ImageHandler.prototype.updateImagePreview = function() {
        const previewContainers = [
            Utils.safeQuerySelector('#feedbackImagePreviewContainer'),
            Utils.safeQuerySelector('#combinedImagePreviewContainer'),
            this.imagePreviewContainer
        ].filter(function(container) {
            return container !== null;
        });

        if (previewContainers.length === 0) {
            console.warn('⚠️ 沒有找到圖片預覽容器');
            return;
        }

        console.log('🖼️ 更新 ' + previewContainers.length + ' 個圖片預覽容器');

        const self = this;
        previewContainers.forEach(function(container) {
            container.innerHTML = '';

            self.images.forEach(function(image, index) {
                const preview = self.createImagePreviewElement(image, index);
                container.appendChild(preview);
            });
        });

        this.updateImageCount();
    };

    /**
     * 創建圖片預覽元素
     */
    ImageHandler.prototype.createImagePreviewElement = function(image, index) {
        const self = this;
        
        // 創建圖片預覽項目容器
        const preview = document.createElement('div');
        preview.className = 'image-preview-item';
        preview.style.cssText = 'position: relative; display: inline-block;';

        // 創建圖片元素
        const img = document.createElement('img');
        img.src = 'data:' + image.type + ';base64,' + image.data;
        img.alt = image.name;
        img.style.cssText = 'width: 80px; height: 80px; object-fit: cover; display: block; border-radius: 6px;';

        // 創建圖片信息容器
        const imageInfo = document.createElement('div');
        imageInfo.className = 'image-info';
        imageInfo.style.cssText = `
            position: absolute; bottom: 0; left: 0; right: 0;
            background: rgba(0, 0, 0, 0.7); color: white; padding: 4px;
            font-size: 10px; line-height: 1.2;
        `;

        const imageName = document.createElement('div');
        imageName.className = 'image-name';
        imageName.textContent = image.name;
        imageName.style.cssText = 'font-weight: bold; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;';

        const imageSize = document.createElement('div');
        imageSize.className = 'image-size';
        imageSize.textContent = Utils.formatFileSize(image.size);
        imageSize.style.cssText = 'font-size: 9px; opacity: 0.8;';

        // 創建刪除按鈕
        const removeBtn = document.createElement('button');
        removeBtn.className = 'image-remove-btn';
        removeBtn.textContent = '×';
        removeBtn.title = '移除圖片';
        removeBtn.style.cssText = `
            position: absolute; top: -8px; right: -8px; width: 20px; height: 20px;
            border-radius: 50%; background: #f44336; color: white; border: none;
            cursor: pointer; font-size: 12px; font-weight: bold;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); transition: all 0.3s ease; z-index: 10;
        `;

        // 添加刪除按鈕懸停效果
        removeBtn.addEventListener('mouseenter', function() {
            removeBtn.style.background = '#d32f2f';
            removeBtn.style.transform = 'scale(1.1)';
        });
        removeBtn.addEventListener('mouseleave', function() {
            removeBtn.style.background = '#f44336';
            removeBtn.style.transform = 'scale(1)';
        });

        // 添加刪除功能
        removeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            self.removeImage(index);
        });

        // 組裝元素
        imageInfo.appendChild(imageName);
        imageInfo.appendChild(imageSize);
        preview.appendChild(img);
        preview.appendChild(imageInfo);
        preview.appendChild(removeBtn);

        return preview;
    };

    /**
     * 更新圖片計數顯示
     */
    ImageHandler.prototype.updateImageCount = function() {
        const count = this.images.length;
        const countElements = document.querySelectorAll('.image-count');

        countElements.forEach(function(element) {
            element.textContent = count > 0 ? '(' + count + ')' : '';
        });

        // 更新上傳區域的顯示狀態
        const uploadAreas = [
            Utils.safeQuerySelector('#feedbackImageUploadArea'),
            Utils.safeQuerySelector('#combinedImageUploadArea')
        ].filter(function(area) {
            return area !== null;
        });

        uploadAreas.forEach(function(area) {
            if (count > 0) {
                area.classList.add('has-images');
            } else {
                area.classList.remove('has-images');
            }
        });
    };

    /**
     * 移除圖片
     */
    ImageHandler.prototype.removeImage = function(index) {
        this.images.splice(index, 1);
        this.updateImagePreview();
    };

    /**
     * 清空所有圖片
     */
    ImageHandler.prototype.clearImages = function() {
        this.images = [];
        this.updateImagePreview();
    };

    /**
     * 獲取圖片數據
     */
    ImageHandler.prototype.getImages = function() {
        return Utils.deepClone(this.images);
    };

    /**
     * 重新初始化（用於佈局模式切換）
     */
    ImageHandler.prototype.reinitialize = function(layoutMode) {
        console.log('🔄 重新初始化圖片處理功能...');
        
        this.layoutMode = layoutMode;
        this.removeImageEventListeners();
        this.initImageElements();
        
        if (this.imageUploadArea && this.imageInput) {
            this.setupImageEventListeners();
            console.log('✅ 圖片處理功能重新初始化完成');
        } else {
            console.warn('⚠️ 圖片處理重新初始化失敗 - 缺少必要元素');
        }
        
        this.updateImagePreview();
    };

    /**
     * 更新設定
     */
    ImageHandler.prototype.updateSettings = function(settings) {
        this.imageSizeLimit = settings.imageSizeLimit || 0;
        this.enableBase64Detail = settings.enableBase64Detail || false;
        
        // 同步到 UI 元素
        if (this.imageSizeLimitSelect) {
            this.imageSizeLimitSelect.value = this.imageSizeLimit.toString();
        }
        if (this.enableBase64DetailCheckbox) {
            this.enableBase64DetailCheckbox.checked = this.enableBase64Detail;
        }
    };

    /**
     * 清理資源
     */
    ImageHandler.prototype.cleanup = function() {
        this.removeImageEventListeners();
        
        if (this.pasteHandler) {
            document.removeEventListener('paste', this.pasteHandler);
            this.pasteHandler = null;
        }
        
        this.clearImages();
    };

    // 將 ImageHandler 加入命名空間
    window.MCPFeedback.ImageHandler = ImageHandler;

    console.log('✅ ImageHandler 模組載入完成');

})();
