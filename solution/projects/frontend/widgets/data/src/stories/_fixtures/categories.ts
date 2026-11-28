import type { TreeNode } from '../../Tree';

export interface Category {
  name: string;
  count?: number;
}

export const CATEGORY_TREE: TreeNode<Category>[] = [
  {
    id: 'electronics',
    data: { name: 'Electronics', count: 1240 },
    children: [
      {
        id: 'computers',
        data: { name: 'Computers', count: 410 },
        children: [
          { id: 'laptops', data: { name: 'Laptops', count: 220 } },
          { id: 'desktops', data: { name: 'Desktops', count: 95 } },
          { id: 'accessories', data: { name: 'Accessories', count: 95 } },
        ],
      },
      {
        id: 'phones',
        data: { name: 'Phones', count: 530 },
        children: [
          { id: 'smartphones', data: { name: 'Smartphones', count: 480 } },
          { id: 'phone-cases', data: { name: 'Cases', count: 50 } },
        ],
      },
      { id: 'audio', data: { name: 'Audio', count: 300 } },
    ],
  },
  {
    id: 'home',
    data: { name: 'Home & Garden', count: 870 },
    children: [
      { id: 'furniture', data: { name: 'Furniture', count: 320 } },
      { id: 'kitchen', data: { name: 'Kitchen', count: 290 } },
      { id: 'garden', data: { name: 'Garden', count: 260 } },
    ],
  },
  {
    id: 'apparel',
    data: { name: 'Apparel', count: 1900 },
    children: [
      { id: 'mens', data: { name: "Men's", count: 800 } },
      { id: 'womens', data: { name: "Women's", count: 900 } },
      { id: 'kids', data: { name: 'Kids', count: 200 } },
    ],
  },
];
