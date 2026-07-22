export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);
      return await env.ASSETS.fetch(url.pathname);
    } catch (e) {
      return new Response('Not Found', { status: 404 });
    }
  },
};
