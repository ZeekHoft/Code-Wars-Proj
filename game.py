from multiprocessing import Process



def game():
    from main import menu
    menu()
def control():
    from run import print_action
    print_action()

def main():


    p1 = Process(target=print_action)
    p1.start()
    
    p2 = Process(target=menu)
    p2.start()
    
    p1.join()
    p2.join()
if __name__ == "__main__":
    main()