import React, { useState, useEffect } from 'react';
import axios from 'axios';

function ProductForm({ existingProduct, onSuccess }) {
  const [name, setName] = useState(existingProduct ? existingProduct.name : '');
  const [description, setDescription] = useState(existingProduct ? existingProduct.description : '');
  const [price, setPrice] = useState(existingProduct ? existingProduct.price : '');
  const [categoryId, setCategoryId] = useState(existingProduct && existingProduct.category ? existingProduct.category.id : '');
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    // Загрузить список категорий для выпадающего списка
    axios.get('/api/categories/')
      .then(res => setCategories(res.data.results || res.data))
      .catch(err => console.error(err));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = { name, description, price, category_id: categoryId };
    if (existingProduct) {
      axios.put(`/api/products/${existingProduct.id}/`, payload)
        .then(() => onSuccess())
        .catch(err => console.error(err));
    } else {
      axios.post('/api/products/', payload)
        .then(() => onSuccess())
        .catch(err => console.error(err));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Название</label>
        <input value={name} onChange={e => setName(e.target.value)} required />
      </div>
      <div>
        <label>Описание</label>
        <textarea value={description} onChange={e => setDescription(e.target.value)} />
      </div>
      <div>
        <label>Цена</label>
        <input type="number" step="0.01" value={price} onChange={e => setPrice(e.target.value)} required />
      </div>
      <div>
        <label>Категория</label>
        <select value={categoryId} onChange={e => setCategoryId(e.target.value)}>
          <option value="">Без категории</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>{cat.name}</option>
          ))}
        </select>
      </div>
      <button type="submit">{existingProduct ? 'Обновить' : 'Создать'}</button>
    </form>
  );
}

export default ProductForm;
