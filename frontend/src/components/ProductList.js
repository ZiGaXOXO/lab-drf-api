import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [nextPageUrl, setNextPageUrl] = useState(null);
  const [prevPageUrl, setPrevPageUrl] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [ordering, setOrdering] = useState('');

  useEffect(() => {
    fetchProducts();
  }, [page, search, ordering]);

  const fetchProducts = () => {
    let url = `/api/products/?page=${page}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (ordering) url += `&ordering=${ordering}`;
    axios.get(url)
      .then(res => {
        setProducts(res.data.results);
        setNextPageUrl(res.data.next);
        setPrevPageUrl(res.data.previous);
      })
      .catch(err => console.error(err));
  };

  const handleDelete = (id) => {
    axios.delete(`/api/products/${id}/`)
      .then(() => fetchProducts())
      .catch(err => console.error(err));
  };

  return (
    <div>
      <h2>Список товаров</h2>
      <div>
        <input
          type="text"
          placeholder="Поиск"
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1); }}
        />
        <select value={ordering} onChange={e => setOrdering(e.target.value)}>
          <option value="">Без сортировки</option>
          <option value="price">Цена ↑</option>
          <option value="-price">Цена ↓</option>
          <option value="name">Название ↑</option>
          <option value="-name">Название ↓</option>
        </select>
      </div>
      <ul>
        {products.map(prod => (
          <li key={prod.id}>
            {prod.name} — {prod.price} — {prod.category ? prod.category.name : 'Нет категории'}
            <button onClick={() => handleDelete(prod.id)}>Удалить</button>
          </li>
        ))}
      </ul>
      <div>
        {prevPageUrl && <button onClick={() => setPage(page-1)}>Назад</button>}
        <span> Страница {page} </span>
        {nextPageUrl && <button onClick={() => setPage(page+1)}>Вперед</button>}
      </div>
    </div>
  );
}

export default ProductList;
