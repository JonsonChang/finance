// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// No Node.js APIs are available in this process because
// `nodeIntegration` is turned off. Use `preload.js` to
// selectively enable features needed in the rendering
// process.

console.log('render.js');

var vm = new Vue({
    el:'#app',
    data:{
        stock_cfgs:null,
        editFondData:{
            S_name:"99",
            sid:"0050",
            best_ma:31,
            Update:"TW",
            test_start_date:"2020/7/1"
        },
        edit_index: 0,
        edit_form_state: "edit" // edit or new
    },
    methods:{
        click_edit: function (stock_idx){
            console.log("edit");
            console.log(stock_idx);
            this.edit_form_state = "edit"
            this.editFondData = this.stock_cfgs[stock_idx];
            this.edit_index = stock_idx;
        },
        click_del: function (stock_idx){
            console.log("del");
            console.log(stock_idx);
            message = this.stock_cfgs[stock_idx].S_name + ' 確定刪除嗎？';
            // if (confirm(message))  //會造成edit 表單無法操作
            {
                a = this.stock_cfgs.splice(stock_idx,1);
                this.stock_cfgs = window.electron.setStockConfig(this.stock_cfgs);
                this.refresh();
            }
        
        },
        click_update: function (stock_idx){
            console.log("update");
            console.log(stock_idx);
            window.electron.updateData(stock_idx);
        },
        click_run_mudel: function (stock_idx){
            console.log("run click_run_mudle");
            console.log(stock_idx);
            window.electron.runModel(stock_idx);
        },
        click_update_all: function (){
            console.log("run click_update_all");
            window.electron.updateAllData();
        },
        click_run_all_model: function (){
            console.log("click_run_all_model");
            window.electron.runAllModel();
        },
        click_add_new_cfg: function (stock_idx){
            console.log("run click_add_new_cfg");
            console.log(stock_idx);
            this.edit_form_state = "new"
            this.editFondData = {
                S_name:"新名稱",
                sid:"0050",
                best_ma:31,
                Update:"TW",
                test_start_date:"2021/6/1"
            };
            this.edit_index = stock_idx;
        },
        click_addnew_form: function (){
            console.log("click_addnew_form");
            this.stock_cfgs.push(this.editFondData);
            this.stock_cfgs = window.electron.setStockConfig(this.stock_cfgs);
            this.refresh();
        },
        saveCfg: function(){
            console.log("saveCfg");
            this.stock_cfgs[this.edit_index] = this.editFondData;
            this.stock_cfgs = window.electron.setStockConfig(this.stock_cfgs);
            this.refresh();
        },
        refresh: function(){this.stock_cfgs = window.electron.getStockConfig();}
    },
    created: function () {
        console.log('vue created');
        this.refresh();
    }
});



window.addEventListener('DOMContentLoaded', () => {
    console.log('dom content load');
});