const path = require('path');
const builder = require('electron-builder');

builder.build({

    projectDir: path.resolve(__dirname),  // 專案路徑 

    win: ['nsis'],  // nsis . //portable 無法存取設定檔案
    config: {
        "appId": "com.andrewdeveloper.electron.cat",
        "productName": "不停損投資", // 應用程式名稱 ( 顯示在應用程式與功能 )
        "directories": {
            "output": "build/win"
        },
        "extraResources": [
            {
              "from": "exe/",
              "to": "exe/"
            }
        ],
        "win": {
            "icon": path.resolve(__dirname, 'icon.png'),
        }
    },
})
    .then(
        data => console.log(data),
        err => console.error(err)
    );