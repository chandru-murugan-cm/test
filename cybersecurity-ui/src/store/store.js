import { configureStore } from "@reduxjs/toolkit";
import { persistStore, persistReducer } from "redux-persist";
import { combineReducers } from "redux";
import storage from "redux-persist/lib/storage";
import authReducer from "./authSlice";
import { projectsApi } from "./api/cyberService/projectApi";
import { scannerApi } from "./api/cyberService/scannerApi";
import { schedulesApi } from "./api/cyberService/scheduleApi";
import { repositoriesApi } from "./api/cyberService/repositoryAPi";
import { domainApi } from "./api/cyberService/domainAPi";
import { repoScanResultsApi } from "./api/cyberService/repoScanResultsApi.js";
import { complianceApi } from "./api/cyberService/complianceAp.js";
import { contractApi } from "./api/cyberService/contractApi.js";
import { sammApi } from "./api/cyberService/sammApi.js";
import { cloudAzureApi } from "./api/cyberService/cloudAzureApi.js";
import { sammUserScoreApi } from "./api/cyberService/sammScoreApi.js";
import { asvsApi } from "./api/cyberService/asvsApi.js";
import { cloudGoogleApi } from "./api/cyberService/cloudGoogleApi.js";
import { vaptReportApi } from "./api/cyberService/vaptReportApi.js";

const persistConfig = {
  key: "root",
  storage,
  whitelist: ["auth"],
};

const rootReducer = combineReducers({
  auth: authReducer,
  [projectsApi.reducerPath]: projectsApi.reducer,
  [scannerApi.reducerPath]: scannerApi.reducer,
  [schedulesApi.reducerPath]: schedulesApi.reducer,
  [repositoriesApi.reducerPath]: repositoriesApi.reducer,
  [domainApi.reducerPath]: domainApi.reducer,
  [repoScanResultsApi.reducerPath]: repoScanResultsApi.reducer,
  [complianceApi.reducerPath]: complianceApi.reducer,
  [contractApi.reducerPath]: contractApi.reducer,
  [sammApi.reducerPath]: sammApi.reducer,
  [cloudAzureApi.reducerPath]: cloudAzureApi.reducer,
  [sammUserScoreApi.reducerPath]: sammUserScoreApi.reducer,
  [asvsApi.reducerPath]: asvsApi.reducer,
  [cloudGoogleApi.reducerPath]: cloudGoogleApi.reducer,
  [vaptReportApi.reducerPath]: vaptReportApi.reducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      sammApi.middleware,
      projectsApi.middleware,
      scannerApi.middleware,
      schedulesApi.middleware,
      repositoriesApi.middleware,
      domainApi.middleware,
      repoScanResultsApi.middleware,
      complianceApi.middleware,
      contractApi.middleware,
      cloudAzureApi.middleware,
      sammUserScoreApi.middleware,
      asvsApi.middleware,
      cloudGoogleApi.middleware,
      vaptReportApi.middleware
    ),
});

const persistor = persistStore(store);

export { store, persistor };
