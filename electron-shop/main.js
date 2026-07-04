const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// 热重载：监听文件变化自动刷新窗口
require('electron-reload')(__dirname, {
    electron: path.join(__dirname, 'node_modules', '.bin', 'electron'),
    hardResetMethod: 'exit'
});

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        minWidth: 800,
        minHeight: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            webSecurity: false
        },
        icon: path.join(__dirname, 'assets/icon.png'),
        title: '在线商城'
    });

    mainWindow.loadFile('renderer/index.html');
    mainWindow.setMenuBarVisibility(false);

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// IPC handlers
ipcMain.handle('login', async (event, { username, password, loginType }) => {
    const response = await fetch('http://127.0.0.1:8000/api/users/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, login_type: loginType })
    });
    return await response.json();
});

ipcMain.handle('get-goods', async (event, params) => {
    const url = new URL('http://127.0.0.1:8000/api/goods/');
    if (params) {
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    }
    const response = await fetch(url);
    return await response.json();
});

ipcMain.handle('get-goods-detail', async (event, id) => {
    const response = await fetch(`http://127.0.0.1:8000/api/goods/${id}/`);
    return await response.json();
});
