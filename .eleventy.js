module.exports = function(eleventyConfig) {
  return {
    dir: {
      input: "src",
      output: "dist",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["njk","md","html","css","json","ico","svg","png","jpg","gif","webp"],
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    dataTemplateEngine: "njk",
    pathPrefix: "/mind-spec/"
  };
};
