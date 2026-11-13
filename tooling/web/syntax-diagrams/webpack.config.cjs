// webpack.config.cjs
const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = (env, argv) => {
  const isProd = argv.mode === "production";

  // For GitHub Pages project sites, assets must be under "/<repo>/"
  // In pages.yml set: PUBLIC_PATH=/${{ github.event.repository.name }}/
  const publicPath = process.env.PUBLIC_PATH ?? (isProd ? "/" : "/");

  return {
    entry: path.resolve(__dirname, "src/main.tsx"),

    output: {
      path: path.resolve(__dirname, "dist"),
      filename: isProd ? "assets/[name].[contenthash].js" : "assets/[name].js",
      clean: true,
      publicPath
    },

    resolve: {
      extensions: [".tsx", ".ts", ".js", ".mjs"],
      fullySpecified: false
    },

    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: {
            loader: "ts-loader",
            options: {
              // Keep transpileOnly for fast builds; typecheck is enforced separately in CI
              transpileOnly: true,
              configFile: path.resolve(__dirname, "tsconfig.webpack.json")
            }
          },
          exclude: /node_modules/
        },
        { test: /\.css$/i, use: ["style-loader", "css-loader"] },
        { test: /\.(png|svg|jpg|jpeg|gif)$/i, type: "asset" }
      ]
    },

    plugins: [
      new HtmlWebpackPlugin({
        template: path.resolve(__dirname, "index.html"),
        publicPath
      })
    ],

    devtool: isProd ? "source-map" : "eval-cheap-module-source-map",

    devServer: {
      port: 5175,
      hot: true,
      historyApiFallback: true,
      client: { overlay: true },
      static: {
        directory: path.resolve(__dirname, "public")
      }
    },

    optimization: { splitChunks: { chunks: "all" } },
    performance: { hints: false }
  };
};
