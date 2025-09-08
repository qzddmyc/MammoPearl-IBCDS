/**
 * 环境标记，表示是否允许后端操作;
 * - flase: 允许; true: 仅展示页面
 * 需要提前引用此文件, 且使用时需要将此变量拷贝, 拷贝件需要二次确认;
 * 用于以下文件:
 * - login.html > login-main.js
 * - detect.html > detect-main.js
 */
const DISABLE_INTERACTION_global = false;