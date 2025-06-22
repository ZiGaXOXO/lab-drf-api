import React from 'react';
import ProductList from './components/ProductList';
import ProductForm from './components/ProductForm';
import ProductCount from './components/ProductCount';

function App() {
  return (
    <div>
      <h1>Управление товарами</h1>
      <ProductForm onSuccess={() => window.location.reload()} />
      <ProductList />
    </div>
  );
}

export default App;
