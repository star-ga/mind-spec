try{require("dotenv").config()}catch{}
const MarkdownIt = require("markdown-it");

module.exports = function(eleventyConfig) {
  const md = new MarkdownIt({ html:true, linkify:true, typographer:true });
  eleventyConfig.addPairedNunjucksShortcode("markdownRender", (content)=> md.render(content || ""));

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "dist" },
    templateFormats: ["njk","md","html"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    dataTemplateEngine: "njk"
  };
};
