/**
 * MCP Feedback Enhanced - Image Handler Module
 * ==============================================
 *
 * Thin wrapper around FileUploadManager for image upload and preview.
 */

(function() {
    'use strict';

    // Ensure namespace exists
    window.MCPFeedback = window.MCPFeedback || {};

    /**
     * ImageHandler constructor
     */
    function ImageHandler(options) {
        options = options || {};

        this.layoutMode = options.layoutMode || 'combined-horizontal';

        // Create file upload manager
        this.fileUploadManager = new window.MCPFeedback.FileUploadManager({
            onFileAdd: function(fileData) {
                console.log('📁 File added:', fileData.name);
            },
            onFileRemove: function(fileData) {
                console.log('🗑️ File removed:', fileData.name);
            }
        });

        console.log('🖼️ ImageHandler initialized');
    }

    /**
     * Initialize
     */
    ImageHandler.prototype.init = function() {
        this.fileUploadManager.initialize();
    };

    /**
     * Get uploaded images
     */
    ImageHandler.prototype.getImages = function() {
        return this.fileUploadManager.getFiles();
    };

    /**
     * Clear all images
     */
    ImageHandler.prototype.clearImages = function() {
        this.fileUploadManager.clearFiles();
    };

    /**
     * Reinitialize (for layout mode switches)
     */
    ImageHandler.prototype.reinitialize = function(layoutMode) {
        this.layoutMode = layoutMode;
    };

    /**
     * Cleanup resources
     */
    ImageHandler.prototype.cleanup = function() {
        this.fileUploadManager.cleanup();
    };

    // Export
    window.MCPFeedback.ImageHandler = ImageHandler;

    console.log('✅ ImageHandler module loaded');

})();
