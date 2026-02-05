from django.core.management.base import BaseCommand
from django.db.models import Count
from questions.models import Category, Question
from users.models import User
from faker import Faker
import random


class Command(BaseCommand):
    help = '生成测试题目和分类数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            type=int,
            default=10,
            help='生成的分类数量'
        )
        parser.add_argument(
            '--questions',
            type=int,
            default=100,
            help='生成的题目数量'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据'
        )

    def handle(self, *args, **options):
        num_categories = options['categories']
        num_questions = options['questions']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('清除现有题目和分类...'))
            Question.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('数据清除完成'))

        fake = Faker('zh_CN')

        self.stdout.write(f'开始生成 {num_categories} 个分类和 {num_questions} 道题目...')

        categories_data = [
            {'name': 'Python', 'parent': None},
            {'name': 'Java', 'parent': None},
            {'name': 'JavaScript', 'parent': None},
            {'name': 'Vue', 'parent': None},
            {'name': 'React', 'parent': None},
            {'name': 'Django', 'parent': None},
            {'name': 'Flask', 'parent': None},
            {'name': 'Spring Boot', 'parent': None},
            {'name': 'MySQL', 'parent': None},
            {'name': 'PostgreSQL', 'parent': None},
            {'name': 'MongoDB', 'parent': None},
            {'name': 'Node.js', 'parent': None},
            {'name': '算法与数据结构', 'parent': None},
        ]

        categories = []
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(f'创建分类: {category.name}')

        sub_categories_data = [
            {'name': 'Python基础', 'parent': categories[0]},
            {'name': 'Python进阶', 'parent': categories[0]},
            {'name': 'Python专题', 'parent': categories[0]},
            {'name': 'Java基础', 'parent': categories[1]},
            {'name': 'Java进阶', 'parent': categories[1]},
            {'name': 'Java专题', 'parent': categories[1]},
            {'name': 'JavaScript基础', 'parent': categories[2]},
            {'name': 'Vue基础', 'parent': categories[3]},
            {'name': 'Vue进阶', 'parent': categories[3]},
            {'name': 'React基础', 'parent': categories[4]},
            {'name': 'Django专题', 'parent': categories[5]},
            {'name': 'Flask专题', 'parent': categories[6]},
            {'name': 'Spring Boot专题', 'parent': categories[7]},
            {'name': '排序算法', 'parent': categories[12]},
            {'name': '树结构', 'parent': categories[12]},
            {'name': '图论', 'parent': categories[12]},
        ]

        for cat_data in sub_categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(f'创建子分类: {category.name}')

        all_categories = list(Category.objects.all())
        users = list(User.objects.filter(is_staff=True))
        if not users:
            users = list(User.objects.all())
        
        default_creator = users[0] if users else None

        question_templates = {
            'Python': [
                '什么是Python？',
                'Python是强类型还是弱类型语言？',
                'Python中的装饰器是什么？',
                '解释Python中的GIL',
                'Python中的列表推导式是什么？',
                'Python中的生成器和迭代器有什么区别？',
                'Python中的深拷贝和浅拷贝有什么区别？',
                'Python中的多线程有什么特点？',
                'Python中的异常处理机制是什么？',
            ],
            'Java': [
                'Java中的接口和抽象类有什么区别？',
                'Java中的多态是如何实现的？',
                'Java中的垃圾回收机制是什么？',
                'Java中的集合框架有哪些？',
                'Java中的线程池是什么？',
                'Java中的反射机制是什么？',
                'Java中的泛型有什么作用？',
                'Java中的注解是什么？',
                'Java中的Lambda表达式是什么？',
            ],
            'JavaScript': [
                'JavaScript中的闭包是什么？',
                'JavaScript中的原型链是什么？',
                'JavaScript中的事件循环是什么？',
                'JavaScript中的Promise是什么？',
                'JavaScript中的async/await是什么？',
                'JavaScript中的this指向问题？',
                'JavaScript中的数组方法有哪些？',
                'JavaScript中的对象解构是什么？',
                'JavaScript中的模块化是什么？',
            ],
            'Vue': [
                'Vue中的响应式原理是什么？',
                'Vue中的生命周期有哪些？',
                'Vue中的组件通信方式有哪些？',
                'Vue中的computed和watch有什么区别？',
                'Vue中的v-if和v-show有什么区别？',
                'Vue中的指令有哪些？',
                'Vue中的路由是什么？',
                'Vue中的状态管理是什么？',
                'Vue中的插槽是什么？',
            ],
            'React': [
                'React中的虚拟DOM是什么？',
                'React中的生命周期有哪些？',
                'React中的Hooks是什么？',
                'React中的useState和useEffect是什么？',
                'React中的组件通信方式有哪些？',
                'React中的Context API是什么？',
                'React中的Redux是什么？',
                'React中的性能优化有哪些？',
            ],
            'Django': [
                'Django中的MVC架构是什么？',
                'Django中的ORM是什么？',
                'Django中的中间件是什么？',
                'Django中的模板引擎是什么？',
                'Django中的表单处理是什么？',
                'Django中的认证系统是什么？',
                'Django中的缓存机制是什么？',
                'Django中的信号是什么？',
            ],
            'Flask': [
                'Flask中的路由是什么？',
                'Flask中的蓝图是什么？',
                'Flask中的模板引擎是什么？',
                'Flask中的请求上下文是什么？',
                'Flask中的会话管理是什么？',
                'Flask中的扩展有哪些？',
            ],
            'Spring Boot': [
                'Spring Boot中的自动配置是什么？',
                'Spring Boot中的starter是什么？',
                'Spring Boot中的依赖注入是什么？',
                'Spring Boot中的AOP是什么？',
                'Spring Boot中的事务管理是什么？',
                'Spring Boot中的REST API是什么？',
            ],
            'MySQL': [
                'MySQL中的索引是什么？',
                'MySQL中的事务是什么？',
                'MySQL中的存储引擎有哪些？',
                'MySQL中的主键和外键是什么？',
                'MySQL中的查询优化有哪些？',
                'MySQL中的备份和恢复是什么？',
            ],
            'PostgreSQL': [
                'PostgreSQL中的JSON类型是什么？',
                'PostgreSQL中的全文搜索是什么？',
                'PostgreSQL中的窗口函数是什么？',
                'PostgreSQL中的CTE是什么？',
                'PostgreSQL中的性能优化有哪些？',
            ],
            'MongoDB': [
                'MongoDB中的文档是什么？',
                'MongoDB中的集合是什么？',
                'MongoDB中的索引是什么？',
                'MongoDB中的聚合框架是什么？',
                'MongoDB中的副本集是什么？',
                'MongoDB中的分片是什么？',
            ],
            '算法与数据结构': [
                '什么是时间复杂度？',
                '什么是空间复杂度？',
                '快速排序的原理是什么？',
                '归并排序的原理是什么？',
                '二叉树的遍历方式有哪些？',
                '图的遍历算法有哪些？',
                '动态规划的基本思想是什么？',
                '贪心算法的基本思想是什么？',
                '哈希表的原理是什么？',
            ],
        }

        answer_templates = {
            'Python': [
                'Python是一种高级编程语言，具有简洁、易读的语法特点。它支持多种编程范式，包括面向对象、函数式和过程式编程。Python广泛应用于Web开发、数据分析、人工智能等领域。',
                'Python是强类型的动态语言。强类型意味着不允许不同类型之间的隐式转换，动态类型意味着变量在运行时确定类型。',
                '装饰器是Python中用于修改函数或类行为的语法糖。它本质上是一个函数，接受一个函数作为参数，返回一个新的函数。',
                'GIL（全局解释器锁）是Python解释器中的一个机制，用于保护对Python对象的访问，防止多线程同时执行Python字节码。',
                '列表推导式是Python中创建列表的简洁语法，它基于一个或多个可迭代对象生成新的列表。',
                '生成器是Python中一种特殊的迭代器，它使用yield关键字生成值。迭代器是实现了__iter__和__next__方法的对象。',
                '浅拷贝只复制对象的引用，而深拷贝会递归复制对象的所有内容。浅拷贝使用copy.copy()，深拷贝使用copy.deepcopy()。',
                'Python的多线程由于GIL的存在，在CPU密集型任务中无法实现真正的并行，但在IO密集型任务中仍然有效。',
                'Python使用try-except-finally结构来处理异常。try块包含可能出错的代码，except块处理异常，finally块总是执行。',
            ],
            'Java': [
                '接口是抽象方法的集合，不能包含实例变量。抽象类可以包含抽象方法和具体方法，可以有实例变量。一个类可以实现多个接口，但只能继承一个抽象类。',
                '多态是面向对象编程的核心概念之一。在Java中，多态通过方法重写和接口实现来实现，允许不同的对象对相同的方法调用做出不同的响应。',
                'Java的垃圾回收机制自动回收不再使用的对象内存。它使用分代回收算法，将对象分为新生代、老年代等，针对不同代使用不同的回收策略。',
                'Java集合框架包括List、Set、Map等接口及其实现类。List是有序集合，Set是不重复集合，Map是键值对集合。',
                '线程池是Java中管理线程的机制，它可以重用线程，减少线程创建和销毁的开销。Java提供了ExecutorService来创建和管理线程池。',
                '反射是Java在运行时获取类信息并操作类或对象的能力。通过反射，可以动态调用方法、访问字段等。',
                '泛型是Java 5引入的特性，它允许在编译时进行类型检查。泛型可以提高代码的类型安全性和可读性。',
                '注解是Java 5引入的元数据机制，它可以在类、方法、字段等元素上添加信息。注解可以被编译器、运行时环境等读取和处理。',
                'Lambda表达式是Java 8引入的函数式编程特性，它允许以更简洁的方式表示匿名函数。Lambda表达式可以用于函数式接口。',
            ],
            'JavaScript': [
                '闭包是指函数能够访问其外部作用域中的变量，即使外部函数已经执行完毕。闭包在JavaScript中常用于数据封装和模块化。',
                '原型链是JavaScript中实现继承的机制。每个对象都有一个原型对象，通过原型链可以访问原型对象的属性和方法。',
                '事件循环是JavaScript中处理异步操作的机制。它包括调用栈、任务队列、微任务队列等部分，负责协调同步和异步代码的执行。',
                'Promise是JavaScript中处理异步操作的对象。它代表一个可能还未完成的操作，并提供then、catch等方法来处理操作的结果或错误。',
                'async/await是JavaScript中处理异步操作的语法糖。它基于Promise，允许以同步的方式编写异步代码，提高代码可读性。',
            ],
            'Vue': [
                'Vue的响应式原理基于Object.defineProperty或Proxy。当数据变化时，Vue会自动更新相关的DOM。Vue 3使用Proxy实现响应式，性能更好。',
                'Vue的生命周期包括创建、挂载、更新、销毁等阶段。常用的生命周期钩子有created、mounted、updated、destroyed等。',
                'Vue组件通信方式包括props、$emit、$refs、provide/inject、Vuex/Pinia等。props用于父传子，$emit用于子传父。',
                'computed是计算属性，基于依赖缓存结果；watch是侦听器，当数据变化时执行回调。computed适合计算属性，watch适合执行副作用。',
                'v-if是条件渲染，会销毁和重建DOM元素；v-show是条件显示，只是切换元素的display属性。v-if有更高的切换开销，v-show有更高的初始渲染开销。',
            ],
            'React': [
                '虚拟DOM是React中的核心概念，它是真实DOM的内存表示。React通过比较虚拟DOM的差异来最小化真实DOM的操作，提高性能。',
                'React类组件的生命周期包括挂载、更新、卸载三个阶段。常用的生命周期方法有componentDidMount、componentDidUpdate、componentWillUnmount等。',
                'Hooks是React 16.8引入的特性，它允许在函数组件中使用状态和其他React特性。常用的Hooks有useState、useEffect、useContext等。',
                'useState用于在函数组件中声明状态，useEffect用于处理副作用。useState返回状态值和更新函数，useEffect接受回调函数和依赖数组。',
            ],
            'Django': [
                'Django的MVC架构实际上是MVT（Model-View-Template）。Model负责数据，View负责业务逻辑，Template负责页面展示。',
                'ORM（对象关系映射）是Django中操作数据库的方式。它允许使用Python对象来表示数据库表，通过方法来执行CRUD操作。',
                '中间件是Django中的钩子机制，它在请求和响应处理过程中执行。中间件可以用于认证、日志、跨域处理等。',
                'Django使用自己的模板引擎，它支持模板继承、过滤器、标签等特性。模板引擎将模板和数据结合生成HTML。',
                'Django提供了Form类来处理表单验证和渲染。Form可以自动生成HTML表单，验证用户输入，并显示错误信息。',
            ],
            'Flask': [
                '路由是Flask中将URL映射到视图函数的机制。使用@app.route装饰器可以定义路由，支持动态URL参数和HTTP方法限制。',
                '蓝图是Flask中组织应用的方式。它允许将应用分割为多个模块，每个模块有自己的路由、模板等。',
            ],
            'Spring Boot': [
                '自动配置是Spring Boot的核心特性，它根据类路径和配置自动配置Spring应用。自动配置减少了手动配置的工作量。',
                'Starter是Spring Boot提供的依赖集合，它包含了特定功能所需的所有依赖。例如，spring-boot-starter-web包含了Web开发所需的所有依赖。',
                '依赖注入是Spring的核心特性，它通过IoC容器管理对象的创建和依赖关系。依赖注入降低了组件之间的耦合度。',
                'AOP（面向切面编程）是Spring中实现横切关注点的方式。它允许将日志、事务、权限等横切逻辑与业务逻辑分离。',
            ],
            'MySQL': [
                '索引是MySQL中提高查询性能的数据结构。它类似于书的目录，可以快速定位数据。索引可以创建在单个列或多个列上。',
                '事务是MySQL中保证数据一致性的机制。事务具有ACID特性：原子性、一致性、隔离性、持久性。',
                'MySQL的存储引擎包括InnoDB、MyISAM、Memory等。InnoDB支持事务和外键，是默认的存储引擎；MyISAM不支持事务，但读取速度快。',
            ],
            'PostgreSQL': [
                'JSON类型是PostgreSQL中存储JSON数据的原生类型。它支持JSON数据的查询、索引和操作，比存储文本更高效。',
                '全文搜索是PostgreSQL中搜索文本内容的功能。它支持中文分词、短语搜索、相关性排序等高级搜索功能。',
            ],
            'MongoDB': [
                '文档是MongoDB中的基本数据单元，类似于关系数据库中的行。文档使用BSON格式存储，支持嵌套结构和数组。',
                '集合是MongoDB中存储文档的容器，类似于关系数据库中的表。集合不需要预定义结构，可以存储不同结构的文档。',
            ],
            '算法与数据结构': [
                '时间复杂度是衡量算法执行时间随输入规模增长的指标。常见的时间复杂度有O(1)、O(log n)、O(n)、O(n log n)、O(n²)等。',
                '空间复杂度是衡量算法所需内存空间随输入规模增长的指标。它与时间复杂度同样重要，特别是在内存受限的环境中。',
                '快速排序是一种分治算法，它选择一个基准元素，将数组分为两部分，递归排序。平均时间复杂度为O(n log n)。',
                '归并排序是一种分治算法，它将数组分成两半，递归排序后合并。时间复杂度为O(n log n)，空间复杂度为O(n)。',
                '二叉树的遍历方式包括前序、中序、后序遍历。前序：根-左-右；中序：左-根-右；后序：左-右-根。',
                '图的遍历算法包括深度优先搜索（DFS）和广度优先搜索（BFS）。DFS使用栈实现，BFS使用队列实现。',
                '动态规划是将问题分解为子问题，通过保存子问题的解来避免重复计算。它适用于具有最优子结构和重叠子问题性质的问题。',
                '贪心算法在每一步选择局部最优解，希望得到全局最优解。它不一定总能得到最优解，但实现简单，效率高。',
                '哈希表是基于键值对存储的数据结构，它通过哈希函数将键映射到存储位置。哈希表的查找、插入、删除操作平均时间复杂度为O(1)。',
            ],
        }

        questions = []
        for i in range(num_questions):
            category = random.choice(all_categories)
            
            category_name = category.name
            if category.parent:
                category_name = category.parent.name
            
            if category_name in question_templates:
                title = random.choice(question_templates[category_name])
                answers = answer_templates.get(category_name, ['这是一个很好的问题，需要深入理解相关概念。'])
                answer = random.choice(answers)
            else:
                title = f'{category_name}相关的问题 {i+1}'
                answer = fake.text(max_nb_chars=200)
            
            existing_questions = Question.objects.filter(title=title)
            if existing_questions.exists():
                continue

            question = Question.objects.create(
                title=title,
                answer=answer,
                category=category,
                creator=default_creator,
                difficulty=random.choice([1, 2, 3]),
                is_approved=True,
                explanation=fake.text(max_nb_chars=100) if random.random() < 0.5 else ''
            )

            questions.append(question)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'已生成 {i + 1}/{num_questions} 道题目')

        self.stdout.write(self.style.SUCCESS(f'题目生成完成: {len(questions)} 道'))

        self.generate_statistics()

    def generate_statistics(self):
        total_categories = Category.objects.count()
        total_questions = Question.objects.count()
        approved_questions = Question.objects.filter(is_approved=True).count()
        
        difficulty_stats = Question.objects.values('difficulty').annotate(
            count=models.Count('id')
        ).order_by('difficulty')

        self.stdout.write(self.style.SUCCESS('\n数据统计:'))
        self.stdout.write(f'  总分类数: {total_categories}')
        self.stdout.write(f'  总题目数: {total_questions}')
        self.stdout.write(f'  已审核题目: {approved_questions}')
        self.stdout.write('  难度分布:')
        for stat in difficulty_stats:
            difficulty_name = {1: '易', 2: '中', 3: '难'}.get(stat['difficulty'], '未知')
            self.stdout.write(f'    {difficulty_name}: {stat["count"]} 道')
