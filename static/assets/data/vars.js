/**
 * 环境标记，表示是否允许后端（服务器）操作;
 * - flase: 允许
 * - true: 仅展示页面
 * 
 * 需要提前引用此文件, 且使用时需要将此变量拷贝, 拷贝件需要二次确认。
 * 用于以下文件:
 * - login.html > login-main.js
 * - detect.html > detect-main.js
 */
const DISABLE_INTERACTION_global = false;

/**
 * localStorage中存放用户名的变量名。使用时无需拷贝。
 * 用于以下文件：
 * - index.html > idx-main.js
 * - login.html > login-main.js
 */
const LocalStorage_DataName = 'usr';