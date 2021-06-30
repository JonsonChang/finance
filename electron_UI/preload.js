// All of the Node.js APIs are available in the preload process.
// It has the same sandbox as a Chrome extension.
const { contextBridge, ipcRenderer } = require('electron')
const { spawn, spawnSync  } = require('child_process');
const fs = require('fs');
const path = require('path');


let isPackaged = ipcRenderer.sendSync('AppIsPacked', {test:123});
console.log(isPackaged);
let BASEDIR = path.resolve(__dirname);
if(isPackaged) {
  BASEDIR = path.resolve(process.resourcesPath);
}

let config_file_path =  path.resolve(BASEDIR, 'exe/config_stock.tw.json');
let exe_model = path.resolve(BASEDIR, 'exe/test_台股_不停損投資模型.exe')
let exe_update = path.resolve(BASEDIR, 'exe/test_台股_update.exe')
let cwd_path = path.resolve(BASEDIR, 'exe')

contextBridge.exposeInMainWorld(
  'electron',
  {
    // doThing: () => ipcRenderer.send('do-a-thing'),
    getStockConfig:getStockConfig,
    setStockConfig:setStockConfig,
    updateData:function(idx) {
      console.log('更新數據');
      console.log(idx);
      const bat = spawn('cmd.exe', ['/c', exe_update, idx],{shell: true, detached: true, windowsHide:true, stdio: 'inherit',cwd: cwd_path});      console.log('done');
      console.log('done');
    },
    updateAllData:function() {
      console.log('更新全部數據');
      const bat = spawn('cmd.exe', ['/c', exe_update],{shell: true, detached: true, windowsHide:true, stdio: 'inherit',cwd: cwd_path});
      console.log('done');
    },
    runModel:function(idx) {
      console.log('執行模型');
      console.log(idx);
      const bat = spawn('cmd.exe', ['/c', exe_model, idx],{shell: true, detached: true, windowsHide:true, stdio: 'inherit',cwd: cwd_path});
      console.log('done');
    },
    runAllModel:function() {
      console.log('執行全部模型');
      const bat = spawn('cmd.exe', ['/c', exe_model],{shell: true, detached: true, windowsHide:true, stdio: 'inherit',cwd: cwd_path});
      console.log('done');
    },
    test: (channel, data)=>{
      console.log('api test', channel, data);
      console.log(exe_update);
      console.log(exe_model);
      console.log(config_file_path);
      console.log(cwd_path);
      console.log(process.cwd());
      console.log(process.execPath);
      console.log(process.resourcesPath);
      console.log(process.env.NODE_ENV)


    }
  },
  "api", {
    send: (channel, data) => {
        // whitelist channels
        let validChannels = ["toMain"];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    },
    receive: (channel, func) => {
        let validChannels = ["fromMain"];
        if (validChannels.includes(channel)) {
            // Deliberately strip event as it includes `sender` 
            ipcRenderer.on(channel, (event, ...args) => func(...args));
        }
    }
  }
)

function getStockConfig() {
   let rawdata = fs.readFileSync(config_file_path);
   let stock_data = JSON.parse(rawdata);
   return stock_data;
}

function setStockConfig(stockData) {
  fs.writeFileSync(config_file_path, JSON.stringify(stockData, null, 4));
}

window.addEventListener('DOMContentLoaded', () => {
  const replaceText = (selector, text) => {
    const element = document.getElementById(selector)
    if (element) element.innerText = text
  }

  for (const type of ['chrome', 'node', 'electron']) {
    replaceText(`${type}-version`, process.versions[type])
  }
})

