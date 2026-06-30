module.exports = {
  root: true,
  env: { browser: true, es2022: true, node: true },
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:react/jsx-runtime",
    "plugin:react-hooks/recommended",
  ],
  ignorePatterns: ["dist", "node_modules", "public", "*.config.js", ".eslintrc.cjs"],
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: { jsx: true },
  },
  settings: {
    react: { version: "detect" },
  },
  plugins: ["react-refresh"],
  rules: {
    // React 19 + Vite: forzar que cada archivo exporte al menos un componente
    // que use JSX para que HMR funcione correctamente.
    "react-refresh/only-export-components": [
      "warn",
      { allowConstantExport: true },
    ],
    // Reglas de React recomendadas (no demasiado estrictas para no romper el resto).
    "react/prop-types": "off",
    "react/no-unescaped-entities": "off",
    "react/display-name": "off",
    // Permitir console en dev (se usa mucho para debugging).
    "no-console": ["warn", { allow: ["warn", "error", "info"] }],
    // Variables no usadas: avisar pero no bloquear.
    "no-unused-vars": ["warn", { argsIgnorePattern: "^_", varsIgnorePattern: "^_" }],
  },
  overrides: [
    {
      // Archivos de configuracion / hooks / utils pueden exportar no-componentes.
      files: ["src/**/*.{js,jsx}"],
      rules: {
        "react-refresh/only-export-components": "off",
      },
    },
  ],
};
