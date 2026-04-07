import { BrowserRouter, Route, Routes } from "react-router-dom";
import ArticleDetail from "./components/ArticleDetail";
import Layout from "./components/Layout";
import NewsFeed from "./components/NewsFeed";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<NewsFeed />} />
          <Route path="/articles/:id" element={<ArticleDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
