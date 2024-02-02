package repository

import (
	"encoding/json"
	_ "errors"
	"fmt"
	"log"
	"strconv"
	"sync"
	"time"

	"context"

	"github.com/pehks1980/cache-serv/internal/pkg/model"
)

type item struct {
	item        string
	Expiration 	int64
}

func (it item) Expired() bool {
	if it.Expiration == 0 {
		return false
	}
	return time.Now().UnixNano() > it.Expiration
}


type cache struct {
	//defaultExpiration time.Duration
	items       map[string]item
}

type MemRepo struct{
	sync.RWMutex
	Cache 			  cache
	defaultExpiration time.Duration
}

type MemConfig struct {
	DefExpiry   string `json:"defexpiry"`
}

func NewMemRepo() *MemRepo {
	var lCache = &cache{
		items: make(map[string]item),
	}

	return &MemRepo{
		Cache: *lCache,
	}
}

func (mr *MemRepo) New (config string) RepoIf{
	// init - filename is not used here
	var myData MemConfig
	err := json.Unmarshal([]byte(config), &myData)
	if err != nil {
		log.Printf("Error unmarshaling JSON:%v \n", err)
		return nil
	}

	var lCache = &cache{
		items: make(map[string]item),
	}

	//durationStr := "5s"

	// Parse the string into a time.Duration
	d,_ := strconv.Atoi(myData.DefExpiry)

	duration := time.Duration(d) * time.Second
	
	fmt.Printf("config expiry time %v\n", duration)

	return &MemRepo{
		Cache: *lCache,
		defaultExpiration: duration,
	}
}

func (mr *MemRepo) Get(getReq string) (string, error) {
	mr.RWMutex.RLock()
	defer mr.RWMutex.RUnlock()

	if Value, ok := mr.Cache.items[getReq]; ok {
		return Value.item, nil
	}

	return "", nil //errors.New("key not found")
}

func (mr *MemRepo) Put(putReq *model.PutValue) error {
	
	mr.RWMutex.Lock()
	var lItem = &item{
		item: putReq.Value,
		Expiration: time.Now().Add(mr.defaultExpiration).UnixNano(),
	}
	mr.Cache.items[putReq.Key] = *lItem
	mr.RWMutex.Unlock()

	return nil
}

func (mr *MemRepo) Vacuum(ctx context.Context) {
	for {
		select {
			case <-ctx.Done():	
			// завершения
			log.Println("Vacuum finished.")
			return

			default:
			time.Sleep(time.Duration(1) * time.Second)

			for key, value := range mr.Cache.items{
				mr.RWMutex.Lock()
				if value.Expired(){
					//remove it from cache
					log.Printf("key %v %v was vacuumed due to expire\n",key, value)
					delete(mr.Cache.items, key);
				}
				mr.RWMutex.Unlock()
			} 

		}
	}

}
