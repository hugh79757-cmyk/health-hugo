export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    return await env.ASSETS.fetch(url.pathname);
  },
};
