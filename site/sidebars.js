module.exports = {
  docsSidebar: [
    {
      type: 'category',
      label: 'BurnCloud',
      collapsed: false,
      link: {type: 'doc', id: 'index'},
      items: [
        {
          type: 'category',
          label: 'HTTP / API',
          collapsed: false,
          items: [
            {
              type: 'category',
              label: 'AI API / Data Plane',
              collapsed: false,
              items: [
                {
                  type: 'doc',
                  id: 'http-api/ai-api-data-plane/get-v1-models',
                  label: 'GET /v1/models',
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};
