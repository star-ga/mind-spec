module.exports = async function svgIcon(name){
  // Minimal async fallback to satisfy Nunjucks async shortcodes
  return `<span class="icon" data-icon="${name}"></span>`;
}
