const MarkdownIt = require("markdown-it");
try { require("dotenv").config(); } catch(e) {}

module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy({ "src/img": "img" });
  eleventyConfig.addPassthroughCopy({ "src/css": "css" });
  eleventyConfig.addPassthroughCopy({ "src/js": "js" });

  const md = new MarkdownIt({ html: true, linkify: true, typographer: true });
  eleventyConfig.addPairedNunjucksShortcode("markdownRender", (content) => md.render(content || ""));

  return {
    dir: { input: "src", includes: "_includes", data: "_data", output: "dist" },
    templateFormats: ["njk","md","html"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    dataTemplateEngine: "njk",
    pathPrefix: "/mind-spec/"
  };
};
