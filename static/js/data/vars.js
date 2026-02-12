/**
 * 环境标记，表示是否允许后端（服务器）操作;
 * - flase: 允许
 * - true: 仅展示页面
 * 
 * 需要提前引用此文件, 且使用时需要将此变量拷贝, 拷贝件需要二次确认。
 * 用于以下文件:
 * - login.html > login-main.js
 * - detect.html > detect-main.js
 * - ques.html > ques-ai.js
 */
export const DISABLE_INTERACTION_global = false;

/**
 * localStorage中存放用户名的变量名。使用时无需拷贝。
 * 用于以下文件：
 * - index.html > idx-main.js
 * - login.html > login-main.js
 * - detect.html > detect-main.js
 */
export const LocalStorage_DataName = 'token';

/**
 * localStorage中用于存放“此时ques.html中应当展示的页面”所用的键名。
 * 取值：
 * - LS_page.normal: 展示"常见问题解答"
 * - LS_page.ai: 展示"AI问答"
 * 
 * 用于以下文件：
 * - ques.html > ques-ai.js
 */
export const LocalStorage_QuesInitPage = 'quesInitPage';
export const LS_page = { normal: 'page-a', ai: 'page-b' };