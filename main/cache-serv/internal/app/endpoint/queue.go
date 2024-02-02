package endpoint

import (
	"encoding/json"
	"log"
	"net/http"

	"github.com/pehks1980/cache-serv/internal/pkg/model"
	cache_serv "github.com/pehks1980/cache-serv/pkg/cache-serv"

	"github.com/gorilla/mux"
)

type queueSvc interface {
	Put(req *model.PutValue) error // записиать json ключ:значение во хранилище
	Get(req *cache_serv.GetValueReq) (*cache_serv.GetValueResp, error) // получить из хранилища значение по ключу
}

// регистрация роутинга путей
func RegisterPublicHTTP(queueSvc queueSvc) *mux.Router {
	//
	r := mux.NewRouter()
	r.HandleFunc("/put/", putToQueue(queueSvc) ).Methods(http.MethodPost)
	r.HandleFunc("/get/", getFromQueue(queueSvc) ).Methods(http.MethodPost)
	return r
}

// вьюха для put
func putToQueue(queueSvc queueSvc) http.HandlerFunc {
	return func(w http.ResponseWriter, request *http.Request) {
		// parse req and call queueSvc.Put(...)
		contentType := request.Header.Get("Content-Type")
		if contentType != "application/json" {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		var item = model.PutValue{}
		//found key, work with body
		err := json.NewDecoder(request.Body).Decode(&item)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		/* if item.Value == "" {
			w.WriteHeader(http.StatusBadRequest)
			return
		} */

		err = queueSvc.Put(&item)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		err = json.NewEncoder(w).Encode(&item)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		log.Printf("put: %v \n", item);

		w.Header().Set("Content-Type", "application/json")
		
	}
}
// вьюха для get
func getFromQueue(queueSvc queueSvc) http.HandlerFunc {
	return func(w http.ResponseWriter, request *http.Request) {
		// parse req and call queueSvc.Get(...)
		contentType := request.Header.Get("Content-Type")
		if contentType != "application/json" {
			w.WriteHeader(http.StatusBadRequest)
			return
		}

		var req = cache_serv.GetValueReq{}
		//found key, work with body
		err := json.NewDecoder(request.Body).Decode(&req)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		
		value, err := queueSvc.Get(&req)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		
		err = json.NewEncoder(w).Encode(value)
		if err != nil {
			w.WriteHeader(http.StatusBadRequest)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		log.Printf("get: %v \n", value);
	}
}
