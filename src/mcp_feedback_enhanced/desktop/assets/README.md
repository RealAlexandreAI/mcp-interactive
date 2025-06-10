# 應用圖標資源

此目錄包含桌面應用的圖標資源文件。

## 需要的圖標文件

### Windows
- `icon.ico` - Windows 圖標文件（多尺寸：16x16, 32x32, 48x48, 256x256）

### macOS  
- `icon.icns` - macOS 圖標文件（多尺寸：16x16 到 1024x1024）
- `entitlements.mac.plist` - macOS 權限配置文件

### Linux
- `icon.png` - Linux 圖標文件（建議 512x512）

### 打包資源
- `dmg-background.png` - macOS DMG 背景圖片（540x380）

## 圖標設計建議

- 使用 MCP Feedback Enhanced 的品牌色彩
- 簡潔明了的設計，在小尺寸下仍然清晰
- 符合各平台的設計規範
- 建議使用矢量圖形作為源文件

## 臨時解決方案

在開發階段，可以使用以下方式創建基本圖標：

1. 使用線上圖標生成器
2. 從現有的 Web UI favicon 轉換
3. 使用系統預設圖標

## 注意事項

- 圖標文件應該放在此目錄中
- electron-builder 會自動處理圖標的打包
- 確保圖標文件的版權合規性
