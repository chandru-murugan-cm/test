import { useEffect } from "react";
import { useLocation } from "react-router-dom";

const ScrollToTop = () => {
  const { pathname, search } = useLocation();

  console.log(pathname, "path name");

  useEffect(() => {
    console.log("triggered");
    window.scrollTo(0, 0);
  }, [pathname, search]);
  return null;
};

export default ScrollToTop;
