const path = require("path");
const webpack = require("webpack");
// const autoprefixer = require("autoprefixer");

const BundleAnalyzerPlugin = require("webpack-bundle-analyzer")
  .BundleAnalyzerPlugin;
const BundleTracker = require("webpack-bundle-tracker");
// const CleanWebpackPlugin = require("clean-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin");
// const SentryCliPlugin = require("@sentry/webpack-plugin");
const UglifyJsPlugin = require("uglifyjs-webpack-plugin");
// const { VueLoaderPlugin } = require("vue-loader");

const devMode = process.env.NODE_ENV !== "production";
const hotReload = process.env.HOT_RELOAD === "1";

const jsRule = {
  test: /\.js$/,
  loader: "babel-loader",
  include: path.resolve("./main/static/js"),
  exclude: /node_modules/,
};

const plugins = [
  new webpack.ProvidePlugin({
    "window.jQuery": "jquery",
    jQuery: "jquery",
    $: "jquery",
  }),
  new BundleTracker({ filename: "./webpack-stats.json" }),
  //   new VueLoaderPlugin(),
  new MiniCssExtractPlugin({
    filename: devMode ? "[name].css" : "[name].[hash].css",
    chunkFilename: devMode ? "[id].css" : "[id].[hash].css",
  }),
  new BundleAnalyzerPlugin({ analyzerMode: "static", openAnalyzer: false }),
  new webpack.HotModuleReplacementPlugin(),
  //   new CleanWebpackPlugin(["./static/dist"]),
  //   new CopyWebpackPlugin([
  //     {
  //       from: "./static/src/images/**/*",
  //       to: path.resolve("./static/dist/images/[name].[ext]"),
  //       toType: "template",
  //     },
  //   ]),
];

module.exports = {
  context: __dirname,
  entry: [
    "@babel/polyfill",
    "./main/static/js/main.js",
    "./main/static/js/student.js",
    "./main/static/js/counsellor.js",
    "./main/static/js/stream_room.js",
  ],
  output: {
    path: path.resolve("./main/static/"),
    filename: "[name]-[hash].js",
    publicPath: hotReload ? "http://localhost:8080/" : "",
  },
  devtool: devMode ? "cheap-eval-source-map" : "source-map",
  devServer: {
    hot: true,
    quiet: false,
    headers: { "Access-Control-Allow-Origin": "*" },
  },
  node: {
    fs: "empty",
  },
  module: { rules: [jsRule] },
  externals: { jquery: "jQuery" },
  plugins,
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        cache: true,
        parallel: true,
        sourceMap: true, // set to true if you want JS source maps
      }),
      new OptimizeCSSAssetsPlugin({}),
    ],
  },
};
