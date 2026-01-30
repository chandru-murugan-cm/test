import { configureStore } from "@reduxjs/toolkit";
import { persistStore, persistReducer } from "redux-persist";
import { combineReducers } from "redux";
import storage from "redux-persist/lib/storage";
import authReducer from "./authSlice";
import { projectsApi } from "./api/cyberService/projectApi";
import { scannerApi } from "./api/cyberService/scannerApi";
import { complianceApi } from "./api/cyberService/complianceAp.js";
import { scantypesApi } from "./api/cyberService/scantypeApi.js";
import { sammApi } from "./api/cyberService/sammApi.js";
import { complianceScannerTypesApi } from "./api/cyberService/ComplianceScannerTypesApi.js";
import { frameworkScannerTypesApi } from "./api/cyberService/FrameworkScannerTypesApi.js";
import { asvsApi } from "./api/cyberService/asvsApi.js";
import { asvsScannerTypeApi } from "./api/cyberService/AsvsScannerTypesApi.js";
import { owaspTopTenApi } from "./api/cyberService/OwaspTopTen.js";
import { owasptoptenScannerTypeApi } from "./api/cyberService/OwaspTopTenScannerTypesApi.js";
import { vaptReportApi } from "./api/cyberService/vaptReportApi.js";
import { userApi } from "./api/authService/userApi.js";

const persistConfig = {
  key: "root",
  storage,
  whitelist: ["auth"],
};



const rootReducer = combineReducers({
  auth: authReducer,
  [projectsApi.reducerPath]: projectsApi.reducer,
  [scannerApi.reducerPath]: scannerApi.reducer,
  [complianceApi.reducerPath]: complianceApi.reducer,
  [scantypesApi.reducerPath]:scantypesApi.reducer,
  [sammApi.reducerPath]: sammApi.reducer,
  [complianceScannerTypesApi.reducerPath]: complianceScannerTypesApi.reducer,
  [frameworkScannerTypesApi.reducerPath]: frameworkScannerTypesApi.reducer,
  [asvsApi.reducerPath]: asvsApi.reducer,
  [asvsScannerTypeApi.reducerPath]:asvsScannerTypeApi.reducer,
  [owaspTopTenApi.reducerPath]: owaspTopTenApi.reducer,
  [owasptoptenScannerTypeApi.reducerPath]: owasptoptenScannerTypeApi.reducer,
  [vaptReportApi.reducerPath]: vaptReportApi.reducer,
  [userApi.reducerPath]: userApi.reducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);


const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      projectsApi.middleware,
      scannerApi.middleware,
      complianceApi.middleware,
      scantypesApi.middleware,
      sammApi.middleware,
      complianceScannerTypesApi.middleware,
      frameworkScannerTypesApi.middleware,
      asvsApi.middleware,
      asvsScannerTypeApi.middleware,
      owaspTopTenApi.middleware,
      owasptoptenScannerTypeApi.middleware,
      vaptReportApi.middleware,
      userApi.middleware
    ),
});

const persistor = persistStore(store);

export { store, persistor };
