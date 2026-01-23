import MarkdownIt from 'markdown-it';

const md = new MarkdownIt({
  html: false,       // 禁用 HTML 标签，防止 XSS 攻击（安全第一）
  linkify: true,     // 自动识别链接，变成可点击的
  breaks: true,      // 自动将换行符转为 <br>，这对聊天很重要
  typographer: true  // 优化排版
});
const defaultRender = md.renderer.rules.link_open || function(tokens, idx, options, env, self) {
  return self.renderToken(tokens, idx, options);
};

md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  // 增加 target="_blank" 属性
  tokens[idx].attrSet('target', '_blank');
  // 增加 rel="noopener noreferrer" (安全属性，防止新页面反向操纵)
  tokens[idx].attrSet('rel', 'noopener noreferrer');
  
  // 调用原来的规则进行渲染
  return defaultRender(tokens, idx, options, env, self);
};
export function renderMarkdown(text) {
  if (!text) return '';
  return md.render(text);
}