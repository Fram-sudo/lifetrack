module.exports = async (params) => {
  const { app } = params;
  await app.workspace.openLinkText("Dashboard", "", false);
};
