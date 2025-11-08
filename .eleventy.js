module.exports = function (eleventyConfig) {
  // Add any custom config you had before here

  return {
    pathPrefix: "/mind-spec/",
    dir: { input: "src", output: "dist" }
  };
};
